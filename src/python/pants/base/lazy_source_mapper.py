# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

from collections import defaultdict
import os

from pants.base.build_environment import get_buildroot
from pants.base.build_file import BuildFile

class LazySourceMapper(object):
  """A utility for lazily making a best-effort mapping of source files to targets that own them.

  This attempts to avoid loading more than needed by lazily searching for and loading BUILD files
  adjacent to or in parent directories (up to the buildroot) of a source to construct a (partial)
  mapping of sources to owning targets.

  If in stop-after-match mode, a search will not traverse into parent directories once an owner
  is identified. THIS MAY FAIL TO FIND ADDITIONAL OWNERS in parent directories, or only find them
  when other sources are also mapped first, which cause those owners to be loaded. Some repositories
  may be able to use this to avoid expensive walks, but others may need to prefer correctness.

  A LazySourceMapper reuses computed mappings and only searches a given path once as
  populating the BuildGraph is expensive, so in general there should only be one instance of it.
  """

  def __init__(self, context, stop_after_match=False):
    """Initialize LazySourceMapper

    :param Context context: A Context object as provided to Task instances.
    """
    self._stop_after_match = stop_after_match
    self._build_graph = context.build_graph
    self._address_mapper = context.address_mapper
    self._source_to_address = defaultdict(set)
    self._mapped_paths = set()
    self._searched_sources = set()

  def _find_owners(self, source):
    """Searches for BUILD files adjacent or above a source in the file hierarchy.
    - Walks up the directory tree until it reaches a previously searched path.
    - Stops after looking in the buildroot.

    If self._stop_after_match is set, stops searching once a source is mapped, even if the parent
    has yet to be searched. See class docstring for discussion.

    :param str source: The source at which to start the search.
    """
    # Bail instantly if a source has already been searched
    if source in self._searched_sources:
      return
    self._searched_sources.add(source)

    root = get_buildroot()
    path = os.path.dirname(source)

    # a top-level source has empty dirname, so do/while instead of straight while loop.
    walking = True
    while walking:
      # It is possible
      if path not in self._mapped_paths:
        candidate = BuildFile.from_cache(root_dir=root, relpath=path, must_exist=False)
        if candidate.exists():
          self._map_sources_from_family(candidate.family())
        self._mapped_paths.add(path)
      elif not self._stop_after_match:
        # If not in stop-after-match mode, once a path is seen visited, all parents can be assumed.
        return

      # See class docstring
      if self._stop_after_match and source in self._source_to_address:
        return

      walking = bool(path)
      path = os.path.dirname(path)

  def _map_sources_from_family(self, build_files):
    """Populate mapping of source to owning addresses with targets from given BUILD files.

    :param iterable<BuildFile> build_files: a family of BUILD files from which to map sources.
    """
    for build_file in build_files:
      address_map = self._address_mapper._address_map_from_spec_path(build_file.spec_path)
      for address, addressable in address_map.values():
        self._build_graph.inject_address_closure(address)
        target = self._build_graph._target_addressable_to_target(address, addressable)
        if target.has_resources:
          for resource in target.resources:
            for item in resource.sources_relative_to_buildroot():
              self._source_to_address[item].add(target.address)

        for target_source in target.sources_relative_to_buildroot():
          self._source_to_address[target_source].add(target.address)
        if not target.is_synthetic:
          self._source_to_address[target.address.build_file.relpath].add(target.address)

  def target_addresses_for_source(self, source, must_find=False):
    """Attempt to find targets which own a source by searching up directory structure to buildroot.

    :param string source: The source to look up.
    """
    self._find_owners(source)
    return self._source_to_address[source]
