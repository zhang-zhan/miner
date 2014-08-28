# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import codecs,json,time
from weibo import *
from hbase import gateway

def parse_user(fpath):
    with codecs.open(fpath, 'r', encoding='utf-8') as fp:
        users = json.load(fp,encoding='utf-8')
        for u in users:
            r_user = UserProfile()
            r_user.load(u)
            batch = r_user.get_batches()
            gateway.applyBatch(batch)

def parse_status(fpath):
    with codecs.open(fpath, 'r', encoding='utf-8') as fp:
        statuses = json.load(fp, encoding='utf-8')
        for s in statuses:
            r_status = Status()
            r_status.load(s)

            batch = r_status.get_batches()
            gateway.applyBatch(batch)

def parse_relation(fpath):
    with codecs.open(fpath, 'r', encoding='utf-8') as fp:
        relations = json.load(fp,encoding='utf-8')
        for r in relations:
            self_uid = r['sourse_id']
            state = r['relationship_state']

            #原始数据文件中，0表示互粉，代表关注，2代表粉丝
            #为了处理方便，将0替换为3
            if state == 0:state=3

            following = []
            followers = []
            if state&0x1==1:
                #当前用户的following
                following = [r]
            if state&0x2==2:
                #当前用户的followers
                followers = [r]

            r_user = Relation()
            r_user.load(self_uid,following,followers)

            batch = r_user.get_batches()
            gateway.applyBatch(batch)

if __name__ == '__main__':

    t_start = time.time()
    print "Begin at:",t_start

    parse_relation('./relation.txt')

    print "Relation finished at:",time.time()

    parse_status('./statuses.txt')




    t_stop = time.time()
    print "Stop at:",t_stop

    cost = 0.0 + t_stop - t_start
    print cost