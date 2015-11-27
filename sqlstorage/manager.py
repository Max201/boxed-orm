#!/usr/bin/env python
# -*- coding: utf-8 -*-
from . import model
from .operator import *


class BaseManager(object):
    model = model.BaseModel

    def __init__(self, table):
        self.table = table

    def __getitem__(self, item):
        if hasattr(self, item) and not item.startswith('_'):
            expr = getattr(self, item)
            return self._filter(expr(), )

    def _filter(self, expression, limit=None, start=0, order=[]):
        sql = 'SELECT * FROM `{}` {}'.format(
            self.table.name,
            'WHERE ' + str(expression) if expression else ''
        )

        return self.table.db(sql)