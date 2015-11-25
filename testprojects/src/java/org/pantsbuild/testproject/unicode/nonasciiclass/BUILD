# Fails with
#   File "/Users/zundel/Src/Pants/src/python/pants/build_graph/target_addressable.py", line 91, in __str__
#    return format_str.format(target_type=self.addressed_type, name=self.addressed_name)
#
#Exception message: 'ascii' codec can't decode byte 0xc3 in position 13: ordinal not in range(128)
#
#jvm_binary(name='UtfNamedClassÆØÅ',
#  source='UtfNamedClassÆØÅ.java',
#)


# Fails with
#  File "/Users/zundel/Src/Pants/src/python/pants/build_graph/target.py", line 562, in create_sources_field
#    filespec = {'globs': [os.path.join(sources_rel_path, src) for src in (sources or [])]}
#  File "/Users/zundel/Src/pants/build-support/pants_dev_deps.venv/bin/../lib/python2.7/posixpath.py", line 73, in join
#    path += '/' + b
#
#
#Exception message: 'ascii' codec can't decode byte 0xc3 in position 14: ordinal not in range(128)
#
#jvm_binary(name='nonasciiclass',
#  source='UtfNamedClassÆØÅ.java',
#)

jvm_binary(name='nonasciiclass',
  dependencies=[
    ':lib',
  ]
)

# fails with
#  File "/Users/zundel/Src/Pants/src/python/pants/base/payload.py", line 102, in _compute_fingerprint
#    fp = field.fingerprint()
#  File "/Users/zundel/Src/Pants/src/python/pants/base/payload_field.py", line 48, in fingerprint
#    self._fingerprint_memo = self._compute_fingerprint()
#  File "/Users/zundel/Src/Pants/src/python/pants/base/payload_field.py", line 155, in _compute_fingerprint
#    hasher.update(source)
#
#Exception message: Problem validating target testprojects.src.java.org.pantsbuild.testproject.unicode.nonasciiclass.lib in testprojects/src/java/org/pantsbuild/testproject/unicode/nonasciiclass: 'ascii' codec can't encode characters in position 84-85: ordinal not in range(128)
#
java_library(name='lib',
  sources=globs('*.java'),
)
