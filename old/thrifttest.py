__author__ = 'jiaodongdong'
#encoding=utf-8
import struct
import chardet
from thrift.transport import *
from hbase import Hbase
from hbase.ttypes import *
from thrift.protocol import TBinaryProtocol
#from parse import *
import os
import json
from user import User
from date2stamp import date2unix



#host = 'cdh-1.cdh.ccpl.psych.ac.cn'
host = '192.168.21.161'
port = '9090'

attrs = {
    'profile': ['name', 'gender', 'created_at', 'created_at_or', 'followers_count', 'friends_count', 'statuses_count', 'favourites_count',
                'bi_followers_count', 'province', 'city', 'location', 'description', 'domain', 'verified',
                'verified_type', 'verified_reason', 'lang', 'geo_enabled', 'allow_all_comment', 'allow_all_act_msg',
                'url', 'profile_url', 'profile_image_url', 'avatar_large', 'avatar_hd']
}

# Connect to HBase Thrift server
transport = TTransport.TBufferedTransport(TSocket.TSocket(host, port))
protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)

# Create and open the client connection
client = Hbase.Client(protocol)
transport.open()

'''
scan = TScan()
tableName = 'sina_status'
i = client.scannerOpenWithScan(tableName, scan, None)
result2 = client.scannerGetList(i, 10)
#print result2
for r in result2:
    print r
    print r.row



rowre = client.scannerGet(i)
while rowre:
    #print rowre[0]
    #print 'THE ROW IS', TRowResult(rowre[0]).row
    for r in rowre:
       # print r
        print r.row
        for f, cc in attrs.iteritems():
                    for c in cc:
                        print "%s:%s" % (f, c), r.columns.get("%s:%s" % (f, c)).value


    rowre = client.scannerGet(i)

client.scannerClose(i)
'''
'''
a = client.getTableNames()
print(a)

f = u'E:/JiaoDongdong/200418.txt'
with open(f, 'rt') as jsonFile:
    t = jsonFile.read()
    users = json.loads(t)
    ind = 0 #统计用户数量
    for i in users:
        u = User(i)
        uid = i['id']
        print(uid)

        mutations = []

        print(uid)
        att = u.__getattr__('user')
        print(att)
        print(type(att))
        att2 = str(att)

        aj = User(att)
        test = aj.__getattr__('id')
        print(test)
        key = struct.pack('<qq', test, uid)
        row = buffer(key)
        print(row)

        mi = Mutation(column="status:%s" % row, value=att2)
        mutations.append(mi)

        client.mutateRow('sina_status', row, mutations, None)

        break
        '''

ro = 10473
rs = struct.pack("<q", ro)
row = buffer(rs)

re = client.getRow('sina_user', row, None)
print re

transport.close()