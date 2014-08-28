# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import struct
from hbase.Hbase import *

class UserTag:
    table_name = 'sina_user'
    column_family = 'tag'
    __slots__ = ['uid','tags']

    def load(self, d, uid=None):
        self.tags = d.get('tags',d)
        self.uid = d.get('id',uid)
        self.utags = dict()
        for t in self.tags:
            weight = t.pop('weight')
            flag = t.pop('flag')
            tag = t[t.keys()[0]]
            self.utags[tag] = weight

    def get_columns(self):
        return {
            'id':self.uid,
            'tags':self.utags
        }

    def get_batches(self):
        mutations = []
        for tag,weight in self.utags.iteritems():
            m = Mutation(column='%s:%s' % (UserTag.column_family,tag), value=weight)
            mutations.append(m)

        key = struct.pack('<q',self.uid)
        result = {
            'tableName': self.table_name,
            'rowBatches': BatchMutation(row=key, mutations=mutations)
        }
        return [result]

    def get_key(self):
        id = int(self.key)
        key = struct.pack('<q', id)
        return buffer(key)