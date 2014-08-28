# -*- coding: utf-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import re
import os
import json
import math
import codecs
from datetime import datetime
from dateutil import parser

folder = u'E:/数据导入/新浪2013年终报告数据/备份profile/'
uidFile = u"E:/数据导入/新浪2013年终报告数据/userIDs.txt"
outputFile = u"E:/数据导入/新浪2013年终报告数据/f_Behave_all.csv"

def getCNPortion(string):
    regex = '[wu2E80-u9FFF]+'
    all = len(string)
    cn = sum( [len(s) for s in re.findall(regex,string) ] )
    return 1 - 1.0*cn/all

now = datetime.now()

features = []

with open(uidFile,'r') as f:
    for line in f:
        uid = line.strip('\r\n\t ')
        fname = folder + uid + '.txt'
        if not os.path.exists(fname):continue
        with codecs.open(fname,'r',encoding='utf-8') as uf:
            u = json.load(uf)
            province = u['province']
            city = u['city']

            feature = (
                u['id'],
                '1' if u['allow_all_act_msg'] else '0',
                '1' if u['allow_all_comment'] else '0',
                '1' if '180/0/' in u['avatar_large'] else '0',
                str(1.0 * u['bi_followers_count'] / u['followers_count']) if u['followers_count']>0 else 0,
                str(1.0 * u['bi_followers_count'] / u['friends_count']) if u['friends_count']>0 else 0,
                str(u['bi_followers_count']),
                '1',
                str(( now.date() - parser.parse(u['created_at'],fuzzy=True).date() ).days),
                str( len( u['description'])  ),
                '1' if u'我' in u['domain'] else '0',
                u['favourites_count'],
                str( len( u['domain'] )),
                '1' if len([val for val in u['domain'] if val in '0123456789'])>0 else '0',
                str( u['favourites_count'] ),
                str( math.log10( u['followers_count']+1 ) ),
                str( math.sin( u['friends_count'] * 4000 / math.pi) ),
                '1' if u['geo_enabled'] else '0',
                '1' if u['domain'] in u['url'] else 0,
                province,
                str( len( u['screen_name'] ) ),
                str( math.log10(u['statuses_count']) ) if u['statuses_count']>0 else '0',
                '1' if u['url'] is not None else '0',
                '1' if u['verified'] else '0',
                str( len ( u['verified_reason'] ) ),
                str(u['verified_type']),
                '1' if 'm'==u['gender'] else '0',
                '2' if province in ['11','12','31','50'] or city=='1' else 1
            )

            features.append(feature)


with open(outputFile,'w') as f:
    for feature in features:
        f.write('\n%s' % feature[0])
        for fe in feature[1:]:
            f.write(',%s' % fe)