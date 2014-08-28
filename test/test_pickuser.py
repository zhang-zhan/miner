# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import codecs,time
from datetime import datetime,timedelta
from collections import OrderedDict

import MySQLdb

import util

from weibo import *

suicide_user_path = "E:/Study/Research-Suicide/Exp-SuicideUsers/ControlGroup/Suicide.txt"
compare_user_path = "E:/Study/Research-Suicide/Exp-SuicideUsers/ControlGroup/Compare.txt"

cfg = {
    'host':     "192.168.21.74",
    'user':     "root",
    'passwd':   "wsi_208",
    "db":       "hq",
    "charset":  "utf8"
}

con = MySQLdb.connect(**cfg)
cur = con.cursor (MySQLdb.cursors.DictCursor)

def load_user(path = suicide_user_path):
    users = OrderedDict()
    with codecs.open(path,encoding='utf-8') as f:
        for line in f:
            line = line.strip(' \t\r\n')
            (uid,name,created_at,gender) = line.split('\t')
            users[uid] = (name,gender, created_at)
    return users


def pick_user(gender, created_at_m, created_at_p):
    sql = "SELECT * FROM sina_user where gender='%s'AND created_at BETWEEN '%s' and '%s' ORDER BY rand() LIMIT 100" % (gender,created_at_m,created_at_p)
    cur.execute(sql)

    results = []
    for user in cur:
        u = UserProfile()
        u.load(user)
        results.append(u)
    return results

if __name__ == '__main__':
    users = load_user()

    max_users = float('inf')
    index = 1

    fp = codecs.open(compare_user_path,mode='w',encoding='utf-8')

    for u,(name,gender,created_at) in users.iteritems():
        if index>max_users : break

        t0 = datetime.strptime(created_at,'%Y/%m/%d')
        t_m = t0 - timedelta(days=2)   #minus
        t_p = t0 + timedelta(days=2)   #plus

        fp.write( 'GROUP%s\t%s\t%s\t%s\t%s\n' % (index,u, name, gender, created_at) )
        results = pick_user(gender, t_m.strftime('%Y/%m/%d'), t_p.strftime('%Y/%m/%d'))
        for r in results:
            u_created_at = util.time2epoch(r.created_at_or)
            u_created_at = time.strftime("%Y/%m/%d", time.localtime(u_created_at))

            fp.write( 'GROUP%s\t%s\t%s\t%s\t%s\n' % (index, r.key, r.name, r.gender,u_created_at) )

        fp.write('\n')
        index += 1