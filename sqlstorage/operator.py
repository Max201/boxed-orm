#!/usr/bin/env python
# -*- coding: utf-8 -*-
from MySQLdb import string_literal


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


class Q(BaseOperator):
    def __init__(self, *args):
        self.expr = filter(lambda a: isinstance(a, BaseExpression), args)
        self.starts = ''

    def __unicode__(self):
        return self.starts + ' AND '.join(map(lambda x: str(x), self.expr))

    def __add__(self, other):
        other.starts = '{} OR '.format(str(self))
        return other


class In(BaseExpression):
    operator = 'IN'

    def _gen_expr(self, concat='AND'):
        expressions = []
        for key in self.expr.keys():
            values = ', '.join([string_literal(i) for i in self.expr[key]])
            expressions.append('`{}` {} ({})'.format(key, self.operator, values))

        return (' {} '.format(concat)).join(expressions)


class NotIn(In):
    operator = 'NOT IN'


class Eq(BaseExpression):
    operator = '='

    def _gen_expr(self, concat='AND'):
        expressions = []
        for key in self.expr.keys():
            expressions.append('`{}` {} {}'.format(key, self.operator, string_literal(self.expr[key])))

        return (' {} '.format(concat)).join(expressions)


class NotEq(Eq):
    operator = '<>'


class Like(BaseExpression):
    operator = 'LIKE'

    def _gen_expr(self, concat='AND'):
        expressions = []
        for key in self.expr.keys():
            expressions.append('`{}` {} "%{}%"'.format(key, self.operator, str(self.expr[key])))

        return (' {} '.format(concat)).join(expressions)


class NotLike(Like):
    operator = 'NOT LIKE'


class Starts(BaseExpression):
    operator = 'LIKE'

    def _gen_expr(self, concat='AND'):
        expressions = []
        for key in self.expr.keys():
            expressions.append('`{}` {} "{}%"'.format(key, self.operator, str(self.expr[key])))

        return (' {} '.format(concat)).join(expressions)


class NotStarts(Like):
    operator = 'NOT LIKE'


class Ends(BaseExpression):
    operator = 'LIKE'

    def _gen_expr(self, concat='AND'):
        expressions = []
        for key in self.expr.keys():
            expressions.append('`{}` {} "%{}"'.format(key, self.operator, str(self.expr[key])))

        return (' {} '.format(concat)).join(expressions)


class NotEnds(Like):
    operator = 'NOT LIKE'


class Greater(BaseExpression):
    operator = '>'

    def _gen_expr(self, concat='AND'):
        expressions = []
        for key in self.expr.keys():
            expressions.append('`{}` {} {}'.format(key, self.operator, string_literal(self.expr[key])))

        return (' {} '.format(concat)).join(expressions)


class Less(Greater):
    operator = '<'