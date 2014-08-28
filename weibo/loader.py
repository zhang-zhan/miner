# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import struct
from weibo import *

decode_map = {
    str : None,
    int : '>i',
    long: '>q',
    bool: '>i'
}

def load_user(dic):
    profile = relation = status = tag = psy = None

    for col,val in dic.iteritems():
        c = bytearray(col)
        #寻找第一个:的位置，这里不应当使用split函数，否则如果qualifier当中含有的byte恰好等于:的ascci值的时候
        #就会被拆分成多个值而非两个
        splitter = c.find(':')
        cf = c[:splitter]
        qualifier = c[splitter+1:]

        if cf=='profile':
            index = UserProfile.attrs.index(qualifier)
            t_type = UserProfile.types[index]
            f = decode_map.get(t_type)

            if f is not None:
                v = struct.unpack(f, val.value)
                if isinstance(v,tuple): v=v[0]  #if unpacked value is tuple, pick the first element.
                if t_type==bool: v=bool(v)      #fix the bool bug, convert from int to bool.
            else:
                v = val.value

            if profile is None: profile = UserProfile()
            qualifier = str(qualifier)
            profile.setattr(qualifier,v)

        elif cf=='relation':
            qualifier = struct.unpack('<q',qualifier)
            if relation is None: relation=dict()
            relation[qualifier] = val.value

        elif cf=='status':
            qualifier = struct.unpack('<qq',qualifier)
            if status is None: status=dict()
            status[qualifier] = val.value

        elif cf=='tag':
            if tag is None: tag=dict()
            tag[qualifier] = val.value

        elif cf=='psy':
            if psy is None: psy=dict()
            psy[qualifier] = val.value

        else:
            raise ValueError('Unknown column family in UserLoader:[%s]!' % cf)

    return (profile,relation,status,tag,psy)


def load_status(dic):
    status = repost = None

    for col,val in dic.iteritems():
        c = bytearray(col)
        #寻找第一个:的位置，这里不应当使用split函数，否则如果qualifier当中含有的byte恰好等于:的ascci值的时候
        #就会被拆分成多个值而非两个
        splitter = c.find(':')
        cf = c[:splitter]
        qualifier = c[splitter+1:]

        if cf=='status':
            index = Status.attrs.index(qualifier)
            t_type = Status.types[index]
            f = decode_map.get(t_type)

            if f is not None:
                v = struct.unpack(f, val.value)
                if isinstance(v,tuple): v=v[0]  #if unpacked value is tuple, pick the first element.
                if t_type==bool: v=bool(v)      #fix the bool bug, convert from int to bool.
            else:
                v = val.value

            if status is None: status = Status()
            qualifier = str(qualifier)
            status.setattr(qualifier,v)

        elif cf=='repost':
            index = Repost.attrs.index(qualifier)
            t_type = Repost.types[index]
            f = decode_map.get(t_type)

            if f is not None:
                if t_type==long and len(val.value)==4: f='<i'
                v = struct.unpack(f, val.value)
                if isinstance(v,tuple): v=v[0]  #if unpacked value is tuple, pick the first element.
                if t_type==bool: v=bool(v)      #fix the bool bug, convert from int to bool.
            else:
                v = val.value

            if repost is None: repost = Repost()
            qualifier = str(qualifier)
            repost.setattr(qualifier,v)

    return (status,repost)