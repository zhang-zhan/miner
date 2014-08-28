# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import struct
from hbase.Hbase import *

class UserPsy:
    table_name = 'sina_user'
    column_family = 'psy'
    __slots__ = ['uid','psy']

    def load(self, uid, psy_annotations):
        '''psy_annotations为用户心理特征维度的标注，包含如下信息：
            psy:心理维度名称
            timestamp:进行测评的时间，用epoch time表示（时区为+0800）
            value:该心理维度特征的值
        '''
        self.uid = uid
        self.annotations = dict()
        for t in psy_annotations:
            psy = t.pop('psy')
            value = t.pop('value')
            timestamp = t.pop('timestamp')

            key = '[%s]%s' % (timestamp,psy)
            self.annotations[key] = value

    def get_columns(self):
        return {
            'id':self.uid,
            'psy':self.annotations
        }

    def get_batches(self):
        mutations = []
        for tag,weight in self.annotations.iteritems():
            m = Mutation(column='%s:%s' % (UserPsy.column_family,tag), value=weight)
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