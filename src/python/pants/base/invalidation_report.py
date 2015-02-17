# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (absolute_import, division, generators, nested_scopes, print_function,
                        unicode_literals, with_statement)

from collections import OrderedDict, namedtuple
from hashlib import sha1


class InvalidationReportManager:
  """Creates a report of all versioned target sets seen in the build."""

  _singleton = None
  @classmethod
  def start_task(cls, task_name, cache_manager):
    """
    :param task_name: Name of the task reporting invalidations
    :param InvalidationCacheManager cache_manager: the cache manager instance being used
    """
    if cls._singleton is None:
      cls._singleton = InvalidationReport()
    return cls._singleton.add_task(task_name, cache_manager)

  @classmethod
  def add_vts(cls, cache_manager, targets, cache_key, valid, phase):
    if cls._singleton:
      cls._singleton.add_vts(cache_manager, targets, cache_key, valid, phase)

  @classmethod
  def report(cls, filename):
    """
    :param string filename: filename to write the report to. If 'None', the report is suppressed
    """
    if cls._singleton:
      cls._singleton.report(filename)

class InvalidationReport:

  class TaskReport:
    class TaskEntry(namedtuple('TaskEntry', ['vts_id', 'target_ids', 'cache_key_id',
                                             'cache_key_hash', 'phase', 'valid'])):
      """
      :param vts_id: A manufactured id for the versioned target set
      :param target_ids: list of string target ids
      :param cache_key_id: cache key from the InvalidationCheck
      :param cache_key_hash: hash of cache_key from the InvalidationCheck
      :param valid: True if the cache_key is valid
      """
      pass

    def __init__(self, task_name, cache_manager, invocation_id):
      self._task_name = task_name
      self.cache_manager = cache_manager
      self._invocation_id = invocation_id
      self._entries = []

    def add(self, targets, cache_key, valid, phase=None):
      if not phase:
        raise ValueError('Must specify a descriptive phase= value (e.g. "init", "pre-check", ...')
      # Manufacture a vts_id from a hash of the target ids
      hasher = sha1()
      [hasher.update(t.id) for t in sorted(targets)]
      vts_id = hasher.hexdigest()[:8]
      self._entries.append(self.TaskEntry(vts_id=vts_id,
                                          target_ids=[t.id for t in targets],
                                          cache_key_id=cache_key.id,
                                          cache_key_hash=cache_key.hash,
                                          valid=valid,
                                          phase=phase))

    def report(self, writer):
      """
      :param BufferedWriter writer: output for the report
      """
      for entry in self._entries:
        for target_id in entry.target_ids:
          writer.write(
            '{invocation_id},{task},{vts_id},{target_id},{cache_key_id},{cache_key_hash},{phase},{valid}\n'
            .format(invocation_id=self._invocation_id,
                    task=self._task_name,
                    vts_id=entry.vts_id,
                    target_id=target_id,
                    cache_key_id=entry.cache_key_id,
                    cache_key_hash=entry.cache_key_hash,
                    phase=entry.phase,
                    valid=entry.valid))

  def __init__(self):
    self._task_reports = []
    self._invocation_id = 0

  def add_task(self, task_name, cache_manager):
    self._invocation_id += 1
    task_report = self.TaskReport(task_name, cache_manager, self._invocation_id)
    self._task_reports.append(task_report)
    return task_report

  def add_vts(self, cache_manager, targets, cache_key, valid, phase):
    """ Add a single VersionedTargetSet entry to the report.
    :param InvalidationCacheManager cache_manager:
    :param CacheKey cache_key:
    :param bool valid:
    :param string phase:
    """
    # NB(Eric Ayers): The cache manager doesn't know the name of the task, so look it up in the
    # task entries.  Each new invocation of a task creates a new task report, so start searching
    # from the end of the list of reports to find the most recent one.
    # Note that this scheme will fail if we add parallelism between 2 tasks of the same type.
    for task_report in reversed(self._task_reports):
      if task_report.cache_manager is cache_manager:
        task_report.add(targets, cache_key, valid, phase)

  def report(self, filename):
    """
    :param string filename: file to write out the report to

    Fields in the report:
      invocation_id: A sequence number that increases each time a task is invoked
      task_name: The name of the task
      vts_id: a manufactured id to identify a VersionedTargetSet (from a hash of all target ids)
      target_id: target id
      cache_key_id: the Id for the cache key
      cache_key_hash: computed hash for the cache key
      phase: What part of the validation check the values were captured
      valid: True if the cache is valid for the VersionedTargetSet
    """
    if filename:
      with open(filename, 'w') as writer:
        writer.write('invocation_id,task_name,vts_id,target_id,cache_key_id,cache_key_hash,phase,valid\n')
        for task_report in self._task_reports:
          task_report.report(writer)

