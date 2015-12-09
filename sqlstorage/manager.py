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
            return self._filter(expr(), key=item)

    def __setitem__(self, key, value):
        if hasattr(self, key) and not key.startswith('_'):
            expr = getattr(self, key)
            self.table.db(expr(value))
            self.table.db.connection.commit()

    def _filter(self, expression, key):
        if isinstance(expression, Query) or isinstance(expression, str):
            return self.table.db(str(expression))

        raise ValueError('Can\'t get query from {}@{} manager method'.format(self.table, key))

    def create(self, fields):
        if not fields:
            return None

        values = {}
        for key in self.table.structure.keys():
            value = fields.get(key, self.table.structure[key].default)
            if not value and not self.table.structure[key].is_null and not self.table.structure[key].is_ai:
                raise ValueError('`{}` can\'t be empty'.format(key))

            values[key] = value

        for key in fields.keys():
            if key not in values:
                raise ValueError('Unknown column {} in table {}'.format(key, self.table.name))

        return Query(Insert(self.table, **values))

    def delete(self, query):
        return Query(Delete(self.table), **{type(a).__name__.lower(): a for a in query})

    def update(self, fields):
        kwargs = {type(a).__name__.lower(): a for a in fields}
        return Query(Update(self.table, **kwargs.pop('dict')), **kwargs)

    def all(self):
        return Query(Select(self.table), order=[self.table.pk.name])

    def first(self):
        return self.all().set_range([0, 1])

    def last(self):
        return self.first().set_order(['-{}'.format(self.table.pk)])

    def random(self):
        return self.all().set_order(['?'])