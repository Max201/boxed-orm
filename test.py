#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlstorage import database, manager
from sqlstorage.operator import *

db = database.Database(password='123', name='game', show_query=True)

db['user']['@update'] = {'nick': 'Max23'}, Where(Like(nick='a')), Range(limit=1)

print db['user']['@all'].fetchall()