__author__ = 'Peter_Howe<haobibo@gmail.com>'

import MySQLdb

cfg = {
    'host':     "192.168.8.1",
    'user':     "psymap",
    'passwd':   "wsi_208",
    "db":       "psymap",
    "charset":  "utf8"
}

con = MySQLdb.connect(**cfg)

def get_cur():
    cur = con.cursor (MySQLdb.cursors.DictCursor)
    return cur