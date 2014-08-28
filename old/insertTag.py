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
from time import time
from ctime import getMtime


output = open("C:/Share/LoadDataConf/tag.log", "a")#存放日志

curList = []
input = open("C:/Share/LoadDataConf/tag_in.txt", "r")#配置文件第一行是host第二行是port剩余行是输入文件件
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

for f in curList:
    #mtime = getMtime(f)
    start = time()
    output.write("%s\n" % f.encode("utf-8"))
    jsonTime = float(0)
    fstart = time()
    tagdict = dict()
    with open(f, 'rt') as jsonFile:
        try:
            t = jsonFile.read()
            tags = json.loads(t)
            #print( len(users) )
            ind = 0
            fstop = time()

            for i in tags:
                try:
                    tid = i['Id']
                    tagdict[tid] = str(i)
                except KeyError:
                    output.write("##tagID_KeyERROR##%s\n" % str(e))
                    continue
        except ValueError as e:
            output.write("##tag_ValueERROR##%s\n" % str(e))
            continue

        flist = str(f).split('SinaUserTag')
        f2 = flist[0] + 'SinaUserHasSinaUserTag' + flist[1]
        output.write("%s\n" % f2.encode("utf-8"))
        with open(f2, 'rt') as jsonFile2:
            try:
                t2 = jsonFile2.read()
                users = json.loads(t2)
                for i in users:
                    try:
                        mutations = []

                        uid = i['SinaUserId']
                        tagid = i['SinaUserTagId']

                        tagst = struct.pack(">q", tagid)
                        col = buffer(tagst)

                        uidst = struct.pack("<q", uid)
                        row = buffer(uidst)

                        m = Mutation(column="tag:%s" % col, value=tagdict[tagid])
                        mutations.append(m)
                        client.mutateRow("sina_user", row, mutations, None)
                    except KeyError:
                        output.write("##User_KeyERROR##%s\n" % str(e))
                        continue

            except ValueError as e:
                output.write("##User_ValueERROR##%s\n" % str(e))
                continue

    stop = time()
    output.write("%s%s%s\n" % ("读取文件耗时：", str(fstop-fstart), "秒"))
    #output.write("%s%s%s\n" % ("JSON解析耗时：", str(jsonTime), "秒"))
    output.write("%s%s%s\n" % ("总共耗时：", str(stop-start), "秒"))

stoptime = time()
output.write("%s%s\n" % (str(stoptime-startime), "秒"))

transport.close()
output.close()