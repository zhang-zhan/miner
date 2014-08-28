# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import struct,json
from datetime import datetime

from hbase.Hbase import *

from weibo import Base

import util

class Status(Base):
    table_name = 'sina_status'
    column_family = 'status'
    attrs = ['key', 'idstr', 'uid', 'text', 'seg', 'c_at_or', 'created_at',
         'reposts_count', 'comments_count', 'attitudes_count',
         'source', 'geo', 'pic_urls', 'annotations', 'truncated', 'r_id']
    types = [None, str, long, str, str, str, int,
        int, int ,int,
        str, str, str, str, bool, long
    ]

    def __init__(self):
        self.batches = []

    def load(self,dic):
        #获取发布微博的用户信息
        uid = 0L
        user = dic.get('user',None)
        if user is None:
            uid = dic.get('id',dic.get('user_id'))
            if uid is None:
                raise ValueError('Data Error: Either User information or user id is expected in the status data!')
            else:
                self.uid = uid
        else:
            from weibo import UserProfile
            uprofile = UserProfile()
            uprofile.load(user)
            uid = long( uprofile.idstr )
            self.uid = uid

            #将用户插入到用户表
            self.batches.extend(uprofile.get_batches())

        self.mid = long( dic.get('idstr',dic.get('id')) )

        #处理转发微博
        r_id = 0
        repost = dic.get('retweeted_status')

        if repost is None:
            pass
        else:
            from weibo import Repost
            #将转发微博存在repost列族
            retweet = Repost()
            retweet.load(self.uid, self.mid, repost)
            #print retweet
            r_id = retweet.id
            self.batches.extend(retweet.get_batches())

            #将转发微博对应的原创微博单独存放一份作为原始微博
            if repost.get('deleted',0)==0:  #如果被转发的微博已经被删除，则不保存为原创微博
                original = Status()
                original.load(repost)
                self.batches.extend(original.get_batches())
        self.r_id = long(r_id)

        #处理其他字段信息
        for attr in Status.attrs:
            v = dic.get(attr)
            if attr=='key':
                v = dic.get('id')
            if v is None:
                if attr in ['reposts_count', 'comments_count', 'attitudes_count']:
                    v = 0
                else:
                    continue

            self.setattr(attr,v)

        ustatus = UserStatuses()
        ustatus.load(self, self.uid)
        self.batches.extend(ustatus.get_batches())

    def setattr(self,attr,v):
        #if attr == 'idstr' and v is None: v = str(id)
        if attr == 'created_at':
            str_original = None
            if isinstance(v,int):   #Epoch Time as int or datetime.datetime
                str_original = util.time2str(v)
            elif isinstance(v,datetime):
                v = util.time2epoch(v)
                str_original = util.time2str(v)
            else:   # str
                str_original = v
                v = util.time2epoch(v)  #创建日期，转换为基于东八区的Epoch整数格式
            #print '%25s\t:=\t%s' % ('c_at_or',v)
            self.__setattr__('c_at_or',str_original)

        #print '%25s\t:=\t%s' % (attr,v)
        self.__setattr__(attr,v)

    def get_key(self):
        key = struct.pack('<qq', self.uid, self.mid)
        return buffer(key)

    def getattr(self,attr):
        #处理特殊字段
        if attr == 'key':
            return long(self.mid)
        elif attr in ['pic_urls', 'annotations', 'geo']:
           try:
                v = getattr(self,attr)
                v = json.dumps(v, ensure_ascii=False, encoding='utf-8')
                return v.encode('utf-8')
           except AttributeError as e:
                return None
        else:
            return self.get_bytes(attr)

    def get_original_value(self,attr):
        #处理特殊字段
        if attr == 'key':
            return int(self.idstr)
        else:
            try:
                v = getattr(self,attr)
            except:
                v = None
            return v

    def __str__(self):
        r = dict()
        for t in Status.attrs:
            r[t] = self.get_original_value(t)
        return json.dumps(r,indent=1,ensure_ascii=False)

class UserStatuses(object):
    table_name = 'sina_user'
    column_family = 'status'
    __slots__ = ['uid', 'qualifier', 'mvalue']

    def load(self, status, uid):
        self.uid = int(uid)
        self.qualifier = status.get_key()

        ustatus = 0L

        r_id = getattr(status,'r_id',0)
        if r_id > 0 : ustatus |= 1

        geo = getattr(status,'geo',None)
        if geo is not None : ustatus |= 2

        pics = getattr(status,'pic_urls',None)
        if pics is not None and len(pics)>0: ustatus |= 4
        if status.reposts_count > 0: ustatus |= 8
        if status.comments_count > 0 : ustatus |= 16
        if status.attitudes_count > 0 : ustatus |= 32

        ustatus <<= 32
        ustatus |= util.now2epoch()

        self.mvalue = struct.pack('>q', ustatus)

    def get_key(self):
        key = struct.pack('<q', self.uid)
        return buffer(key)

    def get_columns(self):
        return {'%s:%s' %(UserStatuses.column_family,self.qualifier) : self.mvalue}

    def get_batches(self):
        key = struct.pack('<q', self.uid)
        mutations = [ Mutation(column="%s:%s" % (UserStatuses.column_family, self.qualifier), value=self.mvalue) ]
        batch = BatchMutation(row=key, mutations=mutations)
        result = {
            'tableName': self.table_name,
            'rowBatches': batch
        }
        return [result]