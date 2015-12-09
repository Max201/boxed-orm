#!/usr/bin/env python
# -*- coding: utf-8 -*-
from MySQLdb import string_literal


def is_table(object):
    return type(object).__name__ == 'Table'


def literal(value=None):
    if not value:
        return 'NULL'
    
    return string_literal(value)


class BaseOperator(object):
    def __unicode__(self):
        return ''

    def __str__(self):
        return self.__unicode__()


class BaseExpression(BaseOperator):
    operator = '='

    def __init__(self, **kwargs):
        self.expr = kwargs

    def __unicode__(self):
        return self._gen_expr()

    def _gen_expr(self):
        return self.operator


class Query(BaseOperator):
    def __init__(self, query, where='', order='', range=None):
        self.where = ''
        self.query = ''
        self.order = ''
        self.range = ''

        self.set_query(query)
        self.set_where(where)
        self.set_order(order)
        self.set_range(range)

    def __unicode__(self):
        if isinstance(self.query, Insert):
            return '{}'.format(self.query)

        query = str(self.query)
        if self.where:
            query += ' {}'.format(self.where)
        if self.order:
            query += ' {}'.format(self.order)
        if self.range:
            query += ' {}'.format(self.range)
        return query

    def __setslice__(self, i, j, sequence):
        print i, j, sequence

    def set_where(self, where):
        # Empty where
        if not where:
            return

        # Where object
        if isinstance(where, Where):
            self.where = where

        # Expression
        elif isinstance(where, BaseOperator):
            self.where = Where(where)

        # Tuple of expressions
        elif isinstance(where, type([])):
            self.where = Where(*where)

        # Equal dict
        elif isinstance(where, dict):
            self.where = Where(Equal(**where))

        else:
            raise ValueError('Unknown where format')

        return self

    def set_order(self, order):
        if isinstance(order, Order):
            self.order = order
        elif isinstance(order, type([])):
            self.order = Order(*order)
        else:
            self.order = Order(order)

        return self

    def set_query(self, query):
        self.query = query
        return self

    def set_range(self, range=None):
        if range is not None:
            if isinstance(range, dict):
                self.range = Range(**range)
            elif isinstance(range, type([])):
                self.range = Range(*range)
            elif isinstance(range, Range):
                self.range = range
            else:
                self.range = ''
        else:
            self.range = ''

        return self


class Values(BaseOperator):
    def __init__(self, **kwargs):
        self.values = kwargs


class Select(BaseOperator):
    def __init__(self, db_table, *args):
        if is_table(db_table):
            self.select = filter(lambda f: f not in 'pk', db_table.columns.keys())
            self.table = db_table.name
        else:
            self.select = args or ['*']
            self.table = db_table

        self.starts = 'SELECT {} FROM `{}`'.format(self._get_selection(), self.table)

    def __unicode__(self):
        return self.starts

    def _get_selection(self):
        selection = []
        for f in self.select:
            if f == '*':
                selection.append(f)
                continue

            selection.append('`{}`'.format(f))

        return ', '.join(selection)


class Delete(BaseOperator):
    def __init__(self, db_table):
        if is_table(db_table):
            self.table = db_table.name
        else:
            self.table = db_table

        self.starts = 'DELETE FROM `{}`'.format(self.table)

    def __unicode__(self):
        return self.starts


class Update(BaseOperator):
    def __init__(self, db_table, **kwargs):
        # Values & Keys
        self.update = kwargs

        # Get table name
        if is_table(db_table):
            self.table = db_table.name
            self.pk = db_table.pk.name
        else:
            self.table = db_table
            self.pk = None

    def __unicode__(self):
        return '{}'.format(self.update_query)

    @property
    def update_query(self):
        return 'UPDATE `{}` SET {}'.format(
            self.table, ', '.join(['`{}` = {}'.format(a, literal(self.update[a])) for a in self.update.keys()])
        )


class Insert(BaseOperator):
    def __init__(self, db_table, **kwargs):
        # Values & Keys
        self.update_values = kwargs.values()

        # Get update keys
        self.update_fields = kwargs.keys()

        # Get table name
        if is_table(db_table):
            self.table = db_table.name
            self.pk = db_table.pk.name
        else:
            self.table = db_table
            self.pk = None

    def __unicode__(self):
        return '{} {}'.format(self.insert, self.values)

    @property
    def insert(self):
        return 'INSERT INTO `{}` ({})'.format(
            self.table, ', '.join(['`{}`'.format(a) for a in self.update_fields])
        )

    @property
    def values(self):
        # Update values
        return 'VALUES ({})'.format(
            ', '.join([literal(a) for a in self.update_values])
        )


class Where(BaseOperator):
    def __init__(self, *args):
        self.expr = filter(lambda a: isinstance(a, BaseExpression), args)
        self.starts = ''

    def __unicode__(self):
        return 'WHERE ' + self.expression

    @property
    def expression(self):
        return self.starts + ' AND '.join(map(lambda x: str(x), self.expr))

    def __add__(self, other):
        other.starts = '{} OR '.format(str(self.expression))
        return other


class In(BaseExpression):
    operator = 'IN'

    def _gen_expr(self, concat='AND'):
        expressions = []
        for key in self.expr.keys():
            values = ', '.join([literal(i) for i in self.expr[key]])
            expressions.append('`{}` {} ({})'.format(key, self.operator, values))

        return (' {} '.format(concat)).join(expressions)


class NotIn(In):
    operator = 'NOT IN'


class Equal(BaseExpression):
    operator = '='

    def _gen_expr(self, concat='AND'):
        expressions = []
        for key in self.expr.keys():
            expressions.append('`{}` {} {}'.format(key, self.operator, literal(self.expr[key])))

        return (' {} '.format(concat)).join(expressions)


class NotEqual(Equal):
    operator = '<>'


class Like(BaseExpression):
    operator = 'LIKE'

    def _gen_expr(self, concat='AND'):
        expressions = []
        for key in self.expr.keys():
            expressions.append('`{}` {} "%%{}%%"'.format(key, self.operator, str(self.expr[key])))

        return (' {} '.format(concat)).join(expressions)


class NotLike(Like):
    operator = 'NOT LIKE'


class Starts(BaseExpression):
    operator = 'LIKE'

    def _gen_expr(self, concat='AND'):
        expressions = []
        for key in self.expr.keys():
            expressions.append('`{}` {} "{}%%"'.format(key, self.operator, str(self.expr[key])))

        return (' {} '.format(concat)).join(expressions)


class NotStarts(Like):
    operator = 'NOT LIKE'


class Ends(BaseExpression):
    operator = 'LIKE'

    def _gen_expr(self, concat='AND'):
        expressions = []
        for key in self.expr.keys():
            expressions.append('`{}` {} "%%{}"'.format(key, self.operator, str(self.expr[key])))

        return (' {} '.format(concat)).join(expressions)


class NotEnds(Like):
    operator = 'NOT LIKE'


class Greater(BaseExpression):
    operator = '>'

    def _gen_expr(self, concat='AND'):
        expressions = []
        for key in self.expr.keys():
            expressions.append('`{}` {} {}'.format(key, self.operator, literal(self.expr[key])))

        return (' {} '.format(concat)).join(expressions)


class Less(Greater):
    operator = '<'


class Order(BaseOperator):
    def __init__(self, *args):
        self.fields = args

    def __unicode__(self):
        if len(self.fields) == 0:
            return ''

        order_by = []
        for f in self.fields:
            if f is None or len(f) < 1:
                continue
            if f == '?':
                order_by.append('RAND()')
                continue
            if f.startswith('-'):
                order_by.append('`{}` DESC'.format(f[1:]))
            elif f.startswith('+'):
                order_by.append('`{}` ASC'.format(f[1:]))
            else:
                order_by.append('`{}` ASC'.format(f))
        order_by = filter(lambda o: len(o) > 0, order_by)
        if len(order_by) > 0:
            return 'ORDER BY {}'.format(', '.join(order_by))
        return ''


class Range(BaseOperator):
    def __init__(self, start=None, limit=None):
        self.start = start or 0
        self.limit = limit or 2**64

    def __unicode__(self):
        if not self.start:
            return 'LIMIT {}'.format(self.limit)
        return 'LIMIT {},{}'.format(self.start, self.limit)