# -*- encoding=utf-8 -*-
__author__ = 'Peter'

import os,codecs
from collections import OrderedDict
from datetime import datetime
import time

base_dir = 'J:/Compare-New'

def get_user_path_list(dir='/'):
    uids = get_lines(base_dir+'/TaskList.txt')

    updic = dict()
    for uid in uids:
        if not dir.startswith('/'):
            dir = '/' + dir
        if not dir.endswith('/'):
            dir = dir + '/'
        updic[uid] = base_dir + dir + uid
    return updic

def get_lines(path_txt):
    lines = set()
    with codecs.open(path_txt,'r',encoding='utf-8-sig') as f:
        for line in f:
            e = line.strip(' \t\r\n')
            if len(e)>0:
                lines.add(e)

    return lines

def time_format(time_str):
    """Process the datetime format in Weibo and return epoch format."""
    #dateti = time_str.replace('[+-]\w\w\w\w\s', '')
    if isinstance(time_str,unicode):
        time_str = time_str.encode()

    if isinstance(time_str,str):
        d = time_str.split(" ")
        zone = d.pop(4) #time zone
        time_str = "%s %s %s %s %s" % tuple(d)
        dtmp = datetime.strptime(time_str, "%a %b %d %X %Y")

        stamp = int(time.mktime(dtmp.timetuple()))
        if zone != "+0800":
            hour = int(zone[1: 3])
            min  = int(zone[3: 5])
            stamp += min*60 + (hour+8)*3600 if zone[0] is '-' else (hour-8)*3600
    else:
        stamp = int(time.mktime(time_str.timetuple()))

    stamp = time.strftime("%Y/%m/%d", time.localtime(stamp))
    return stamp