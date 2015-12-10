#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlstorage import database, manager
from sqlstorage.operator import *

db = database.Database(password='123', name='game', show_query=True)

print db(Query(Select(db['user']), Where(Like(password='123')))).fetchall()