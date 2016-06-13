# coding=utf-8
# Copyright 2016 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (absolute_import, division, generators, nested_scopes, print_function,
                        unicode_literals, with_statement)

import unittest

from pants.option.config_list_parser import ConfigListParser


class ConfigListParserTest(unittest.TestCase):

  def setUp(self):
    self.parser = ConfigListParser()

  def assert_parser(self, input, expected_result):
    result = self.parser.parse(input)
    self.assertEquals(result, expected_result,
                      msg="Result {} is: {} Error is {}".format(input, result, self.parser.error_msg()))

  def test_list(self):
    self.assert_parser("[]", [])
    self.assert_parser("['Hello']", ['Hello'])
    self.assert_parser("[\"Hello\"]", ['Hello'])
    self.assert_parser("['Foo','Bar']", ['Foo','Bar'])
    self.assert_parser('["Foo","Bar"]', ['Foo','Bar'])
