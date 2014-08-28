#coding:utf-8
__author__ = 'jiaodongdong'
import struct
import chardet

class User:
    def __init__(self, d):
        self.d = d

    def __getattr__(self, attr):
        try:
            v = self.d[attr]
            if attr is 'verified_type':
                return str(v)
            if isinstance(v, bool):
                key2 = struct.pack('>?', v)
                row2 = buffer(key2)
                return row2
            if isinstance(v, int):
                key2 = struct.pack('>i', v)
                row2 = buffer(key2)
                return row2
            if v == '':
                return None
            if isinstance(v, basestring):
                if isinstance(v, unicode):
                    v = v.encode('utf-8')
        except KeyError as e:
            v = None
        return v