# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

python_library(
  name='option',
  sources=globs('*.py', exclude=['config_list_parser_tab.py']),
  dependencies=[
    '3rdparty/python:ansicolors',
    '3rdparty/python:ply',
    '3rdparty/python:six',
    '3rdparty/python/twitter/commons:twitter.common.collections',
    'src/python/pants/base:build_environment',
    'src/python/pants/base:deprecated',
    'src/python/pants/util:eval',
    'src/python/pants/util:meta',
    'src/python/pants/util:strutil',
    # TODO(zundel): Figure out how to include this file in the build but exclude from style checking
    #':config_list_parser_tab'
  ]
)

# This is a generated file that gets created by the ply library.
# Its a separate target so we can exclude it from the python checkstyle step
python_library(
  name='config_list_parser_tab',
  sources=['config_list_parser_tab.py'],
  dependencies=[
    '3rdparty/python:ply',
  ],
)

target(
  name='migrate_config',
  dependencies=[
    'migrations/options/src/python:migrate_config'
  ]
)
