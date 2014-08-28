# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import codecs,os,json
from collections import defaultdict
from datetime import datetime,timedelta
from textmind import wenxin
import util

suicide_user_path = "G:/Suicide-Program/Weibo/Suicide/"
output_dir = "G:/Features-TimeSequence"

def list_user():
    fs = os.listdir(suicide_user_path)
    result = []
    for f in fs:
        if not f.endswith('.json'): continue
        result.append(suicide_user_path+f)
    return result

def dig_user(fpath):
    with codecs.open(fpath, 'r', encoding='utf-8-sig') as fp:
        statuses = json.load(fp,encoding='utf-8-sig')

        temp = {}

        for s in statuses:
            uid = s['user']['id']
            name = s['user']['screen_name']

            text = s['text']

            time = s['created_at']
            time = util.time2epoch(time)
            time = datetime.fromtimestamp(time)

            (year, week, _) = time.isocalendar()
            key = "%04d%02d" % (year,week)
            tval = temp.get(key,None)
            if tval is not None:
                temp[key] = tval + '\n' + text
            else:
                temp[key] = text

        output_file = '%s/%s.txt' % (output_dir, uid)
        sorted_k = sorted(temp.iterkeys())

        with codecs.open(output_file,'w',encoding='ascii') as fp:
            for k in sorted_k:
                v = temp[k]
                t = wenxin.TextMind()
                v = v.encode('utf-8')
                r = t.process_paragraph(v,encoding='utf-8')
                fp.write( "%s\t%s\n" % (k, repr(r)) )

if __name__ == '__main__':
    users = list_user()
    for u in users:
        dig_user(u)