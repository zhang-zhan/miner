# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import struct
from thrift.transport import *
from hbase import Hbase
from hbase.ttypes import *
import util

from weibo import loader

cfg = {
    #'host' : '192.168.21.173',
    'host' : '192.168.21.51',
    'port' : 9090
}

def fetch(hbase_cfg=cfg):
    # Connect to HBase Thrift server
    transport = TTransport.TBufferedTransport(TSocket.TSocket(cfg['host'], cfg['port']))
    transport.open()

    # Create and open the client connection
    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    client = Hbase.Client(protocol)

    key = struct.pack('<q',2474190592)
    key = buffer(key)
    #results = client.getRow('sina_user',key, None)
    results = client.getRowWithColumns('sina_user',key, ['relation','status','profile'],None)

    for result in results:
        print "RowKey:[%s]" %  util.unpack_little_endian(result.row)
        (profile,relation,status,tag,psy) = loader.load_user(result.columns)
        #print profile
        #print relation
        #print status
        #print tag
        #print psy

    key = struct.pack('<qq',1785450710,3532715665978890)
    key = buffer(key)
    #results = client.getRow('sina_status', key, None)
    results = client.getRowWithColumns('sina_status',key, ['status','repost'],None)
    for result in results:
        uid,mid = util.unpack_little_endian(result.row)
        print "RowKey:[uid=%s][mid=%s]" %  (uid,mid)
        (status, repost) = loader.load_status(result.columns)
        #print status
        #print repost



    transport.close()

if __name__ == '__main__':
    fetch()