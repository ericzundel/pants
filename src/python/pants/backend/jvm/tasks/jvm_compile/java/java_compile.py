# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (absolute_import, division, generators, nested_scopes, print_function,
                        unicode_literals, with_statement)

import os

from pants.backend.jvm.targets.jar_dependency import JarDependency
from pants.backend.jvm.tasks.jvm_compile.analysis_tools import AnalysisTools
from pants.backend.jvm.tasks.jvm_compile.java.jmake_analysis import JMakeAnalysis
from pants.backend.jvm.tasks.jvm_compile.java.jmake_analysis_parser import JMakeAnalysisParser
from pants.backend.jvm.tasks.jvm_compile.jvm_compile import JvmCompile
from pants.base.build_environment import get_buildroot
from pants.base.exceptions import TaskError
from pants.base.workunit import WorkUnitLabel
from pants.java.distribution.distribution import DistributionLocator
from pants.util.dirutil import relativize_paths, safe_mkdir


# From http://kenai.com/projects/jmake/sources/mercurial/content
#  /src/com/sun/tools/jmake/Main.java?rev=26
# Main.mainExternal docs.

_JMAKE_ERROR_CODES = {
   -1: 'invalid command line option detected',
   -2: 'error reading command file',
   -3: 'project database corrupted',
   -4: 'error initializing or calling the compiler',
   -5: 'compilation error',
   -6: 'error parsing a class file',
   -7: 'file not found',
   -8: 'I/O exception',
   -9: 'internal jmake exception',
  -10: 'deduced and actual class name mismatch',
  -11: 'invalid source file extension',
  -12: 'a class in a JAR is found dependent on a class with the .java source',
  -13: 'more than one entry for the same class is found in the project',
  -20: 'internal Java error (caused by java.lang.InternalError)',
  -30: 'internal Java error (caused by java.lang.RuntimeException).'
}
# When executed via a subprocess return codes will be treated as unsigned
_JMAKE_ERROR_CODES.update((256 + code, msg) for code, msg in _JMAKE_ERROR_CODES.items())


class JmakeCompile(JvmCompile):
  """Compile Java code using JMake."""
  _name = 'java'
  _file_suffix = '.java'
  _supports_concurrent_execution = False

  _JMAKE_MAIN = 'org.pantsbuild.jmake.Main'

  @classmethod
  def get_args_default(cls, bootstrap_option_values):
    workdir_gen = os.path.relpath(os.path.join(bootstrap_option_values.pants_workdir, 'gen'),
                                  get_buildroot())
    return ('-C-encoding', '-CUTF-8', '-C-g', '-C-Tcolor',
            # Don't warn for generated code.
            '-C-Tnowarnprefixes',
            '-C{0}'.format(workdir_gen),
            # Suppress warning for annotations with no processor - we know there are many of these!
            '-C-Tnowarnregex', '-C^(warning: )?No processor claimed any of these annotations: .*')

  @classmethod
  def get_warning_args_default(cls):
    return ('-C-Xlint:all', '-C-Xlint:-serial', '-C-Xlint:-path', '-C-deprecation')

  @classmethod
  def get_no_warning_args_default(cls):
    return ('-C-Xlint:none', '-C-nowarn')

  @classmethod
  def register_options(cls, register):
    super(JmakeCompile, cls).register_options(register)
    register('--use-jmake', advanced=True, action='store_true', default=True,
             fingerprint=True,
             help='Use jmake to compile Java targets')
    cls.register_jvm_tool(register,
                          'jmake',
                          classpath=[
                            JarDependency(org='org.pantsbuild', name='jmake', rev='1.3.8-10'),
                          ])
    cls.register_jvm_tool(register,
                          'java-compiler',
                          classpath=[
                            JarDependency(org='org.pantsbuild.tools.compiler',
                                          name='java-compiler',
                                          rev='0.0.1'),
                          ])

  @classmethod
  def subsystem_dependencies(cls):
    return super(JmakeCompile, cls).subsystem_dependencies() + (DistributionLocator,)

  def select(self, target):
    return self.get_options().use_jmake and super(JmakeCompile, self).select(target)

  def __init__(self, *args, **kwargs):
    super(JmakeCompile, self).__init__(*args, **kwargs)
    self.set_distribution(jdk=True)

    self._buildroot = get_buildroot()

    # The depfile is generated by org.pantsbuild.tools.compiler.Compiler
    # and includes information about package-private classes -- e.g.
    # the case where Foo.java also defines class Bar.  This allows jmake
    # to correctly include these files in its analysis.
    self._depfile_folder = os.path.join(self.workdir, 'jmake-depfiles')

  @property
  def _depfile(self):
    safe_mkdir(self._depfile_folder)
    return os.path.join(self._depfile_folder, 'global_depfile')

  def create_analysis_tools(self):
    return AnalysisTools(DistributionLocator.cached().real_home, JMakeAnalysisParser(),
                         JMakeAnalysis)

  def compile(self, args, classpath, sources, classes_output_dir, upstream_analysis, analysis_file,
              log_file, settings):
    relative_classpath = relativize_paths(classpath, self._buildroot)
    jmake_classpath = self.tool_classpath('jmake')
    args = [
      '-classpath', ':'.join(relative_classpath),
      '-d', classes_output_dir,
      '-pdb', analysis_file,
      '-pdb-text-format',
      ]
    # TODO: This file should always exist for modern jmake installs; this check should
    # be removed via a Task-level identity bump after:
    # https://github.com/pantsbuild/pants/issues/1351
    if os.path.exists(self._depfile):
      args.extend(['-depfile', self._depfile])

    compiler_classpath = self.tool_classpath('java-compiler')
    args.extend([
      '-jcpath', ':'.join(compiler_classpath),
      '-jcmainclass', 'org.pantsbuild.tools.compiler.Compiler',
      ])

    if not self.get_options().colors:
      filtered_args = filter(lambda arg: not arg == '-C-Tcolor', self._args)
    else:
      filtered_args = self._args
    args.extend(filtered_args)
    args.extend(settings.args)

    if '-C-source' in args:
      raise TaskError("Define a [jvm-platform] with the desired 'source' level instead of "
                      "supplying one via 'args'.")
    if '-C-target' in args:
      raise TaskError("Define a [jvm-platform] with the desired 'target' level instead of "
                      "supplying one via 'args'.")

    source_level = settings.source_level
    target_level = settings.target_level
    if source_level:
      args.extend(['-C-source', '-C{0}'.format(source_level)])

    if target_level:
      args.extend(['-C-target', '-C{0}'.format(target_level)])

    args.append('-C-Tdependencyfile')
    args.append('-C{}'.format(self._depfile))

    jvm_options = list(self._jvm_options)

    args.extend(sources)
    result = self.runjava(classpath=jmake_classpath,
                          main=JmakeCompile._JMAKE_MAIN,
                          jvm_options=jvm_options,
                          args=args,
                          workunit_name='jmake',
                          workunit_labels=[WorkUnitLabel.COMPILER])
    if result:
      default_message = 'Unexpected error - JMake returned {}'.format(result)
      raise TaskError(_JMAKE_ERROR_CODES.get(result, default_message))
