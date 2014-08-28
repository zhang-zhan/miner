# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import json
import MySQLdb

from weibo import *

cfg = {
    'host':     "192.168.21.74",
    'user':     "root",
    'passwd':   "wsi_208",
    "db":       "weibo_2000",
    "charset":  "utf8"
}

con = MySQLdb.connect(**cfg)
cur = con.cursor (MySQLdb.cursors.DictCursor)

def test_user():
    cur.execute('SELECT * FROM sina_user where length(verified_reason)>0 and length(url)>0 LIMIT 10')
    for user in cur:
        u = UserProfile()
        u.load(user)
        r = u.get_columns()
        print json.dumps(r,ensure_ascii=False, indent=1,sort_keys=True)

def test_status():
    cur.execute('select * from sina_statuses limit 10')
    for status in cur:
        s = Status()
        s.load(status)
        r = s.get_columns()
        print json.dumps(r,ensure_ascii=False, indent=1,sort_keys=True)

if __name__ == '__main__':
    #test_user()
    test_status()