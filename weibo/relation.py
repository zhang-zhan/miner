# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import struct
from hbase.Hbase import *

import util
from weibo import UserProfile

verified_type_map = {
    -1:32,
    220:31,
    200:30
}

class Relation:
    tableName = 'sina_user'
    column_family = 'relation'

    def load(self, self_uid, following=None, followers=None):
        ''' self_uid: 当前用户的UID，用于存储关系。因为需要考虑关注、被关注，故需要此信息；
            following：一个Collection，每个对象为一个用户，Collection为主（源）用户关注了其他的哪些用户；
            followers：一个Collection，每个对象为一个用户，Collection为主（源）用户被其他哪些用户关注（即粉丝）'''
        if following is None and followers is None: raise ValueError('Following and Followers cannot both be None!')
        self.self_uid  = self_uid

        self.uids = dict()
        self.users = dict()

        if following is not None:
            self.following = following
            for u in following:
                uid = u['id']
                self.users[uid] = u
                self.uids[uid] = 1   #对Following，先设定为1

        if followers is not None:
            self.followers = followers
            for u in followers:
                uid = u['id']
                if uid not in self.users: self.users[uid]=u
                self.uids[uid] = 2 if uid not in self.uids else 3 #互粉为3，否则（Followers）为2

    def get_columns(self):
        return {
            'relation': self.ids,
            'profile':self.users
        }

    def get_batches(self):
        #用于存储需要更新的内容，可能涉及多个表、多个列族
        batches = []

        #根据关系用户，将关系用户的Profile插入到表中
        for uid, user in self.users.iteritems():
            uprofile = UserProfile()
            uprofile.load(user)
            batches_uprofile = uprofile.get_batches()
            batches.extend(batches_uprofile)

        #根据关系情况，把用户的id插入到sina_user:relation列族中
        mutations = []
        for uid,relation in self.uids.iteritems():
            qualifier = struct.pack('<q',uid)

            user = self.users[uid]
            gender = user['gender']
            vt = user['verified_type']
            vt = verified_type_map.get(vt,vt)
            v = vt << 3
            v |= 4L if gender == 'm' else 0L
            v |= relation

            v <<= 32
            v |= util.now2epoch()

            v = struct.pack('>q',v)
            m = Mutation(column="%s:%s" % (Relation.column_family,qualifier), value=v)
            mutations.append(m)
        key = struct.pack('<q',self.self_uid)

        u_relation = {
            'tableName': Relation.tableName,
            'rowBatches': BatchMutation(row=key, mutations=mutations)
        }
        batches.append(u_relation)

        return batches