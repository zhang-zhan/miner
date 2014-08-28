# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import struct,json
from hbase.ttypes import *

class Base(object):
    #def __init__(self):
    #    raise TypeError('The abstract Base class shall not be instantiated!')

    def get_bytes(self, attr):
        '''自定义方法，用于将字段值输出为HBase所需的数据存储类型'''
        v = getattr(self,attr, None)

        if v is None or v == '':     #如果值为None或者空串，不保存其值
            return None
        f = None
        if isinstance(v, basestring) and isinstance(v, unicode): #如果是basestring且为unicode格式
            v = v.encode('utf-8')
        elif isinstance(v, int):  #如果是整数，以big-endian的整数类型存储
            f = '>i'
        elif isinstance(v, long):
            f = '>q'
        elif isinstance(v, bool):  #如果是布尔类型，以bool类型存储
            f = '>?'
        if f is not None: v = buffer(struct.pack(f, v))

        return v

    def get_key(self):
        raise TypeError('This method shall be implemented in children classes rather than abstract class!')

    def get_columns(self):
        cols = dict()
        for attr in self.attrs:
            v = getattr(self, attr, None)
            #if attr == 'key': continue
            if v is None: continue
            cols['%s:%s' % (self.column_family, attr)] = v
        return cols

    def get_batches(self):
        #return a list of batch
        mutations = []
        for attr in self.attrs:
            if attr == 'key': continue #避免再将key存入
            v = self.getattr(attr)
            if v is None: continue
            m = Mutation(column="%s:%s" % (self.column_family, attr), value=v)
            mutations.append(m)

        batch = BatchMutation(row=self.get_key(), mutations=mutations)
        result = {
            'tableName': self.table_name,
            'rowBatches': batch
        }

        try:
            batches = getattr(self,'batches')
            if isinstance(batches, list):
                batches.append(result)
            else:
                raise ValueError('Unknown type for batches attribute!')
        except AttributeError as e:
            batches = [result]

        return batches