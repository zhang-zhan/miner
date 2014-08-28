# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import struct,json
from datetime import datetime

import util
from weibo import Base

class UserProfile(Base):
    table_name = 'sina_user'
    column_family = 'profile'
    attrs = ['key', 'idstr',
        'name', 'gender', 'created_at','description', 'domain', 'url', 'profile_url',
        'followers_count', 'friends_count', 'statuses_count', 'favourites_count', 'bi_followers_count',
        'geo_enabled', 'allow_all_comment', 'allow_all_act_msg', 'verified', 'verified_type', 'verified_reason',
        'province', 'city', 'location', 'profile_image_url', 'avatar_large', 'avatar_hd', 'lang',
        #created_at_or: 留存created_at的原始字段的原始字符串类型
        'created_at_or']

    types = [long, str,
        str, str, int, str, str, str, str,
        int, int, int, int, int,
        bool, bool, bool, bool, str, str,
        str, str, str, str, str, str, str,
        str
    ]

    def __init__(self):
        self.batches = []

    def load(self, dic):
        for attr in UserProfile.attrs:
            v = dic.get(attr)
            if attr=='key':
                v = dic.get('id')
            if v is None:continue
            self.setattr(attr,v)

        #如果用户Profile信息包含有其最新的一条微博的信息
        status = dic.get('status')
        if status is None: return
        from weibo import Status
        s = Status()
        s.load(status)
        batches = s.get_batches()
        self.batches.extend(batches)

    def setattr(self,attr,v):
        if attr in ['province','city','verified_type'] and not isinstance(v,str):
            #认证类别、省、市ID用用str存储
            v = str(v)
        elif attr == 'idstr' and v is None:
            v = str(id)
        elif attr == 'created_at':
            str_original = None
            if isinstance(v,int):   #Epoch Time as int or datetime.datetime
                str_original = util.time2str(v)
            elif isinstance(v,datetime):
                v = util.time2epoch(v)
                str_original = util.time2str(v)
            else:   # str
                str_original = v
                v = util.time2epoch(v)  #创建日期，转换为基于东八区的Epoch整数格式
            #print '%25s\t:=\t%s' % ('created_at_or',v)
            self.__setattr__('created_at_or',str_original)

        #print '%25s\t:=\t%s' % (attr,v)
        self.__setattr__(attr,v)

    def getattr(self,attr):
        #处理特殊字段
        if attr == 'key':
            return int(self.key)
        else:
            return self.get_bytes(attr)

    def get_original_value(self,attr):
        #处理特殊字段
        if attr == 'key':
            return int(self.idstr)
        else:
            v = getattr(self,attr, None)
        return v

    def get_key(self):
        id = int(self.key)
        key = struct.pack('<q', id)
        return buffer(key)

    def __str__(self):
        r = dict()
        for t in self.attrs:
            r[t] = self.get_original_value(t)
        return json.dumps(r,indent=1,ensure_ascii=False)