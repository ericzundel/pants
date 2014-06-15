# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

import os
import unittest2 as unittest


class Utf8HeaderTest(unittest.TestCase):

  def test_file_have_coding_utf8(self):
    """
    Look through all .py files and ensure they start with the line '# coding=utf8'
    """
    # TODO(Eric Ayers) Is this the right way to find the real root dir?
    dir = os.getcwd()
    #self.assertFalse(True, "dir is {dir}".format(dir=dir))

    nonconformingFiles = []
    for root, dirs, files in os.walk(dir):
      if root.find(os.sep + "build-support") >= 0:
        continue
      for file in files:
        if file.endswith(".py"):
          path = root + os.sep + file;
          pyFile = open(path, "r")
          firstLine = pyFile.readline()
          if not firstLine.rstrip() == "# coding=utf-8":
            nonconformingFiles.append(path)

    if len(nonconformingFiles) > 0:
      self.fail('Expected these files to contain first line "# coding=utf8" ' + str(nonconformingFiles) )


