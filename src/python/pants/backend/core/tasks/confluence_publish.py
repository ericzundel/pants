# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (absolute_import, division, generators, nested_scopes, print_function,
                        unicode_literals, with_statement)

import os
import textwrap

from twitter.common.confluence import Confluence, ConfluenceError

from pants import binary_util
from pants.backend.core.targets.doc import Page
from pants.backend.core.tasks.task import Task
from pants.base.exceptions import TaskError
from pants.util.dirutil import safe_open


class ConfluencePublish(Task):
  """A task to publish Page targets to Confluence wikis."""

  @classmethod
  def register_options(cls, register):
    super(ConfluencePublish, cls).register_options(register)

    # TODO: https://github.com/pantsbuild/pants/issues/395:
    # url should probably be a param of the wiki, not a config.
    register('--url', help='The url of the confluence site to post to.')
    register('--force', action='store_true', default=False,
             help='Force publish the page even if its contents is '
                   'identical to the contents on confluence.')
    register('--open', action='store_true', default=False,
             help='Attempt to open the published confluence wiki page in a browser.')
    register('--user', help='Confluence user name, defaults to unix user.')

  @classmethod
  def prepare(cls, options, round_manager):
    round_manager.require('wiki_html')

  def __init__(self, *args, **kwargs):
    super(ConfluencePublish, self).__init__(*args, **kwargs)

    self.url = self.get_options().url
    if not self.url:
      raise TaskError('Unable to proceed publishing to confluence. Please set the url option.')

    self.force = self.get_options().force
    self.open = self.get_options().open
    self._wiki = None
    self.user = self.get_options().user

  def wiki(self):
    raise NotImplementedError('Subclasses must provide the wiki target they are associated with')

  def api(self):
    return 'confluence1'

  def execute(self):
    pages = []
    targets = self.context.targets()
    for target in targets:
      if isinstance(target, Page):
        for wiki_artifact in target.payload.provides:
          pages.append((target, wiki_artifact))

    urls = list()

    genmap = self.context.products.get('wiki_html')
    for page, wiki_artifact in pages:
      html_info = genmap.get((wiki_artifact, page))
      if len(html_info) > 1:
        raise TaskError('Unexpected resources for {}: {}'.format(page, html_info))
      basedir, htmls = html_info.items()[0]
      if len(htmls) != 1:
        raise TaskError('Unexpected resources for {}: {}'.format(page, htmls))
      with safe_open(os.path.join(basedir, htmls[0])) as contents:
        url = self.publish_page(
          page.address,
          wiki_artifact.config['space'],
          wiki_artifact.config['title'],
          contents.read(),
          # Default to none if not present in the hash.
          parent=wiki_artifact.config.get('parent')
        )
        if url:
          urls.append(url)
          self.context.log.info('Published {} to {}'.format(page, url))

    if self.open and urls:
      binary_util.ui_open(*urls)

  def publish_page(self, address, space, title, content, parent=None):
    body = textwrap.dedent('''

    <!-- DO NOT EDIT - generated by pants from {} -->

    {}
    ''').strip().format(address, content)

    pageopts = dict(
      versionComment = 'updated by pants!'
    )
    wiki = self.login()
    existing = wiki.getpage(space, title)
    if existing:
      if not self.force and existing['content'].strip() == body.strip():
        self.context.log.warn("Skipping publish of '{}' - no changes".format(title))
        return

      pageopts['id'] = existing['id']
      pageopts['version'] = existing['version']

    try:
      page = wiki.create_html_page(space, title, body, parent, **pageopts)
      return page['url']
    except ConfluenceError as e:
      raise TaskError('Failed to update confluence: {}'.format(e))

  def login(self):
    if not self._wiki:
      try:
        self._wiki = Confluence.login(self.url, self.user, self.api())
      except ConfluenceError as e:
        raise TaskError('Failed to login to confluence: {}'.format(e))
    return self._wiki
