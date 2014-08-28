#coding:utf-8
import struct
#import codecs
#codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)
import chardet

import os
import json
from user import User
from date2stamp import date2unix
from time import time

from weibo.transport import *
from hbase import Hbase
from hbase.ttypes import *
from weibo.protocol import TBinaryProtocol

attrs = {
    'profile': ['name', 'gender', 'created_at', 'followers_count', 'friends_count', 'statuses_count', 'favourites_count',
                'bi_followers_count', 'province', 'city', 'location', 'description', 'domain', 'verified',
                'verified_type', 'verified_reason', 'lang', 'geo_enabled', 'allow_all_comment', 'allow_all_act_msg',
                'url', 'profile_url', 'profile_image_url', 'avatar_large', 'avatar_hd']
}

output = open("C:/Share/LoadDataConf/write.log", "a")#存放日志

curList = []
input = open("C:/Share/LoadDataConf/input.txt", "r")#配置文件第一行是host第二行是port剩余行是输入文件件
host = input.readline().strip('\n')
port = input.readline().strip('\n')
while 1:
    curDirt = input.readline().strip('\n').decode("utf-8")
    if not curDirt:
        break
    curList.append(curDirt)
input.close()

host = host.decode("utf-8")

# Connect to HBase Thrift server
transport = TTransport.TBufferedTransport(TSocket.TSocket(host, port))
protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)

# Create and open the client connection
client = Hbase.Client(protocol)
transport.open()

a = client.getTableNames()
print(a)
output.write("%s\n" % a)

startime = time()

for curDir in curList:
    filesList = os.listdir(curDir)
    for ftmp in filesList:
        f = curDir+'/'+ftmp
        start = time()
        output.write("%s\n" % f.encode("utf-8"))
        jsonTime = float(0)
        fstart = time()
        with open(f, 'rt') as jsonFile:
            t = jsonFile.read()
            users = json.loads(t)
            ind = 0 #统计用户数量
            fstop = time()
            for i in users:
                jstart = time() #count
                u = User(i)
                uid = i['id']
                key = struct.pack('<q', uid)
                row = buffer(key)
                #存储原始id为string
                idstr = i['idstr']
                if isinstance(idstr, unicode):
                    idstr = idstr.encode('utf-8')
                mutations = []
                mi = Mutation(column="profile:idstr", value=idstr)
                mutations.append(mi)

                for f, cc in attrs.iteritems():
                    for c in cc:
                        v = u.__getattr__(c)
                        if v is None:
                            continue
                        if c is 'created_at':
                            #存储原始的created_at
                            m = Mutation(column="%s:%s" % (f, 'created_at_or'), value=v)
                            mutations.append(m)
                            sd = date2unix(v)
                            ke = struct.pack('>i', sd)
                            ro = buffer(ke)
                            m = Mutation(column="%s:%s" % (f, c), value=ro)
                            mutations.append(m)
                        else:
                            m = Mutation(column="%s:%s" % (f, c), value=v)
                            mutations.append(m)
                #time the json spend time
                jstop = time()
                jsonTime = jsonTime + jstop - jstart

                client.mutateRow('sina_user', row, mutations, None)

                ind += 1
                #if ind > 10:
                    #break
            print ind
            output.write("%s%i\n" % ("用户数量：", ind))
        stop = time()
        output.write("%s%s%s\n" % ("读取文件耗时：", str(fstop-fstart), "秒"))
        output.write("%s%s%s\n" % ("JSON解析耗时：", str(jsonTime), "秒"))
        output.write("%s%s%s\n" % ("总共耗时：", str(stop-start), "秒"))
        #break

stoptime = time()
output.write("%s%s\n" % (str(stoptime-startime), "秒"))

transport.close()
output.close()

