#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Column(object):
    def __init__(self, table, name, type, null=False, key=None, default=None, extra=None):
        self.table = table

        # Column properties
        self.name = name
        self.type = type.lower()
        self.null = null
        self.key = key.lower()
        self.default = default
        self.extra = extra.lower()

    def __unicode__(self):
        return '{}#{}'.format(str(self.table), self.name)

    def __str__(self):
        return self.__unicode__()

    @property
    def is_pk(self):
        return self.key in 'pri'

    @property
    def is_null(self):
        return self.null

    @property
    def is_ai(self):
        return self.extra in 'auto_increment'

    @property
    def sql(self):
        return 'ALTER TABLE `{}` ADD `{}` {}'.format(self.table.name, self.name, self.type)