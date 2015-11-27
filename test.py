#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlstorage import database, manager
from sqlstorage.operator import *

db = database.Database(password='123', name='game', show_query=True)


class ManagerCustom(manager.BaseManager):
    def all(self):
        return ''

    def max(self):
        return Q(Like(nick='max'))


db['user']['@'] = ManagerCustom
print db['user']['@all'].fetchall()