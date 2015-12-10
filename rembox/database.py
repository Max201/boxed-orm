#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import MySQLdb
import datetime
import MySQLdb.cursors


class Database(object):
    def __init__(self, user='root', password='', host='localhost', port=3306, name='database', show_query=False):
        self.connection = MySQLdb.connect(
            host=host,
            db=name,
            port=port,
            user=user,
            passwd=password,
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor
        )

        self.show_queries = show_query
        self.query_count = 0

        self.name = name
        self.user = user
        self.host = host
        self.password = password
        self.port = port
        self.tables = self._get_tables()
        self.structure = self._build_structure()

    def __call__(self, query, *args):
        start = self._time_stamp()
        cursor = self.connection.cursor()
        cursor.execute(str(query), args)
        self.query_count += 1
        if self.show_queries:
            print ('[SQL:QUERY][{:.5f}] ' + debug.info('{}; args={}')).format(self._time_stamp() - start, query, args)
        return cursor

    def __unicode__(self):
        return 'db://{}@{}:{}/{}'.format(self.user, self.host, self.port, self.name)

    def __str__(self):
        return self.__unicode__()

    def __getitem__(self, item):
        if item in self.tables:
            return self.structure[item]

        raise IndexError('Undefined table "{}"'.format(item))

    def __setitem__(self, key, value):
        raise ValueError('Cannot create or modify db scheme')

    def __len__(self):
        return len(self.tables)

    def _get_tables(self):
        return [i.values()[0] for i in self('SHOW TABLES').fetchall()]

    def _build_structure(self):
        structure = dict()
        for t in self.tables:
            structure[t] = table.Table(self, t)

        return structure

    @staticmethod
    def _time_stamp():
        now = datetime.datetime.now()
        return time.mktime(now.timetuple()) + now.microsecond / 1000000.0