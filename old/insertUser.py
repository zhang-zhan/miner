__author__ = 'jiaodongdong'
#coding:utf-8
import struct
#import codecs
#import chardet
from weibo.transport import *
from hbase import Hbase
from hbase.ttypes import *
from weibo.protocol import TBinaryProtocol
#from parse import *
import os
import json
from user import User
from date2stamp import date2unix
from ctime import getMtime
import time

attrs = {
    'profile': ['name', 'gender', 'created_at', 'followers_count', 'friends_count', 'statuses_count', 'favourites_count',
                'bi_followers_count', 'province', 'city', 'location', 'description', 'domain', 'verified',
                'verified_type', 'verified_reason', 'lang', 'geo_enabled', 'allow_all_comment', 'allow_all_act_msg',
                'url', 'profile_url', 'profile_image_url', 'avatar_large', 'avatar_hd']
}

output = open("C:/Share/LoadDataConf/User.log", "a")#存放日志


curList = []
input = open("C:/Share/LoadDataConf/user_in.txt", "r")#配置文件第一行是host第二行是port剩余行是输入文件件
host = input.readline().strip('\n')
port = input.readline().strip('\n')
while 1:
    curDirt = input.readline().strip('\n').decode("utf-8")
    if not curDirt:
        break
    curList.append(curDirt)
input.close()

outputerror = open("C:/Share/LoadDataConf/user_in_error.txt", "a")
outputerror.write("%s\n" % host)
outputerror.write("%s\n" % port)
outputerror.close()

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

startime = time.time()

for f in curList:
    mtime = getMtime(f)
    output.write("%s\n" % f.encode("utf-8"))

    with open(f, 'rt') as jsonFile:
        try:
            t = jsonFile.read()
            users = json.loads(t)
            ind = 0 #统计用户数量

            for i in users:

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



                client.mutateRow('sina_user', row, mutations, None)

                ind += 1
                #if ind > 10:
                    #break
            print ind
        except ValueError as e:
            output.write("## ValueERROR ##%s\n" % str(e))
            continue
        except MemoryError as e:
            output.write("## MemoryERROR ##%s\n" % str(e))
            outputerror = open("C:/Share/LoadDataConf/status_in_error.txt", "a")
            outputerror.write("%s\n" % f)
            outputerror.close()
            time.sleep(60)
            continue
        except IOError as e:
            output.write("## IOERROR ##%s\n" % str(e))
            outputerror = open("C:/Share/LoadDataConf/status_in_error.txt", "a")
            outputerror.write("%s\n" % f)
            outputerror.close()
            time.sleep(30)
            continue