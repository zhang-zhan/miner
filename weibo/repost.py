# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import struct,json
from datetime import datetime
from weibo import *
import util

class Repost(Base):
    table_name = 'sina_status'
    column_family = 'repost'
    attrs = ['id', 'uid', 'text', 'seg', 'c_at_or', 'created_at',
         'reposts_count', 'comments_count', 'attitudes_count',
         'source', 'geo', 'pic_urls', 'annotations', 'truncated']

    types = [long, long, str, str, str, int,
        int, int, int,
        str, str, str, str, bool
    ]

    def __init__(self):
        self.batches = []

    def load(self, repost_uid, repost_mid, dic):
        self.repost_uid = repost_uid
        self.repost_mid = repost_mid

        uid = None
        deleted = dic.get('deleted',None)
        if deleted is None: #转发的微博没有被删除
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

        else:   #转发的微博已经被删除
            self.id = uid = 0

        if uid>0:
            for attr in Repost.attrs:
                v = dic.get(attr)
                if attr == 'id': v = long(v)
                if v is None:
                    if attr in ['reposts_count', 'comments_count', 'attitudes_count']:
                        v = 0
                    else:
                        continue

                self.setattr(attr,v)

            ustatus = UserStatuses()
            ustatus.load(self, uid)
            self.batches.extend(ustatus.get_batches())

    def setattr(self,attr,v):
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
        #处理转发微博的key
        key = struct.pack('<qq', self.repost_uid, self.repost_mid)
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
        #print self.text

        #处理特殊字段
        if attr == 'key':
            return self.id
        else:
            try:
                v = getattr(self,attr)
            except:
                v = None
            return v

    def __str__(self):
        r = dict()
        for t in Repost.attrs:
            r[t] = self.get_original_value(t)
        return json.dumps(r,indent=1,ensure_ascii=False)