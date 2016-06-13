# coding=utf-8
# Copyright 2016 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (absolute_import, division, generators, nested_scopes, print_function,
                        unicode_literals, with_statement)

import ply.lex as lex
import ply.yacc as yacc


tokens = (
  #'PLUS', 'MINUS',
  'LBRACKET','RBRACKET',
  'COMMA',
  'SINGLE_QUOTE_ITEM',
  'DOUBLE_QUOTE_ITEM',
)

# Tokens
#t_PLUS    = r'\+'
#t_MINUS   = r'-'
t_LBRACKET  = r'\['
t_RBRACKET = r'\]'
t_COMMA = r','
t_SINGLE_QUOTE_ITEM    = r"'(\\'|[^'])*'"
t_DOUBLE_QUOTE_ITEM    = r'"(\\"|[^"])+"'


def t_error(t):
  ConfigListParser._error_msg = "Illegal character '%s'" .format(t.value[0])

# Parsing rules

precedence = (
)


def p_item_single_quote(t):
  """item : SINGLE_QUOTE_ITEM
          | DOUBLE_QUOTE_ITEM
  """
  t[0] = t[1][1:-1]  # strip off quotes


def p_list_empty(t):
  """list : LBRACKET RBRACKET"""
  t[0] = []


def p_list_one_item(t):
  """list : LBRACKET items RBRACKET"""
  t[0] = t[2]


def p_items_one(t):
  """items : item"""
  t[0] = [t[1]]


def p_items_multiple(t):
  """items : item COMMA items"""
  t[0] = [t[1]] + t[3]


def p_expression(t):
  """expression : list"""
  t[0] = t[1]


def p_error(t):
  ConfigListParser._error_msg = "Syntax error at '{}'".format(t.value)


class ConfigListParser(object):
  _error_msg = None

  def __init__(self, debug=None):
    self.lexer = lex.lex(debug=debug)
    self.parser = yacc.yacc(start='expression', tabmodule='config_list_parser_tab')

  def parse(self, value):
    self._error_msg = None
    self.lexer.input(value)
    if not self.is_error():
      return self.parser.parse(lexer = self.lexer)
    return None

  def error_msg(self):
    return ConfigListParser._error_msg

  def is_error(self):
    return ConfigListParser._error_msg is not None
