#!/usr/bin/env python
# -*- coding: utf-8 -*-
from . import column
from . import manager


class Table(object):
    def __init__(self, db, tablename):
        self.db = db
        self.name = tablename

        # Structure properties
        self.pk = None

        # Build structure
        self.columns = self._get_columns()
        self.structure = self._build_structure()

        # Manager instance
        self.manager = manager.BaseManager(self)

    def clear(self):
        return self.db('TRUNCATE `{}`'.format(self.name))

    def __unicode__(self):
        return '{}/{}'.format(str(self.db), self.name)

    def __str__(self):
        return self.__unicode__()

    def __len__(self):
        return self.db('SELECT COUNT(*) as `__len` FROM `{}`'.format(self.name)).fetchone()['__len']

    def __getitem__(self, item):
        if type(item).__name__ in ['long', 'int']:
            return self.db('SELECT * FROM `{}` WHERE `id`={}'.format(self.name, item))

        if type(item).__name__ not in ['str', 'unicode']:
            raise IndexError('Unknown index type in table {}'.format(self.name))

        if item.startswith('@'):
            return self.manager[item[1:]]

        return self._get_column(item[1:])

    def __setitem__(self, key, value):
        if type(key).__name__ not in ['str', 'unicode']:
            raise IndexError('Unknown index type in table {}'.format(self.name))

        if key in '@':
            return self._set_manager(value)

        if key.startswith('@'):
            self.manager[key[1:]] = value

    def _set_manager(self, mngr):
        mngr = mngr(self)
        if not isinstance(mngr, manager.BaseManager):
            raise ValueError('Invalid manager instance')

        self.manager = mngr

    def _get_column(self, col_name):
        if col_name not in self.columns:
            raise AttributeError('Unknown column {} in table {}'.format(col_name, self.name))

        return self.structure[col_name]

    def _get_columns(self):
        columns = self.db('DESCRIBE `{}`'.format(self.name)).fetchall()
        struct = dict()
        for col in columns:
            struct[col['Field']] = col

        return struct

    def _build_structure(self):
        structure = dict()
        for col in self.columns.keys():
            data = self.columns[col]
            structure[col] = column.Column(
                table=self,
                name=col,
                type=data['Type'],
                null='no' not in data['Null'].lower(),
                key=data['Key'],
                extra=data['Extra']
            )

            if structure[col].is_pk:
                self.pk = structure[col]
        return structure

    def _remove_col(self, col_name):
        new_struct = dict()
        columns = dict()

        for col in self.columns.keys():
            if col == col_name:
                continue

            new_struct[col] = self.structure[col]
            columns[col] = self.columns[col]

        self.structure = new_struct
        self.columns = columns

        return True