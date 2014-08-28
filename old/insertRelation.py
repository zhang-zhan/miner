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



output = open("C:/Share/LoadDataConf/relation.log", "a")#存放日志

curList = []
input = open("C:/Share/LoadDataConf/relation_in.txt", "r")#配置文件第一行是host第二行是port剩余行是输入文件件
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
    mtime = getMtime(f)
    start = time()
    output.write("%s\n" % f.encode("utf-8"))
    jsonTime = float(0)
    fstart = time()
    with open(f, 'rt') as jsonFile:
        try:
            t = jsonFile.read()
            users = json.loads(t)
            #print( len(users) )
            ind = 0
            fstop = time()
            for i in users:
                jstart = time() #count

                ustatus = 0L
                ustatus = ustatus + mtime

                try:
                    mutations = []

                    uid = i['sourse_id']
                    uids = struct.pack("<q", uid)
                    row = buffer(uids)

                    sid = i['id']
                    sids = struct.pack("<q", sid)
                    col = buffer(sids)

                    rs = i['relationship_state']
                    if rs is 0:
                        ustatus |= 1L << 32
                        ustatus |= 1L << 33
                    elif rs is 1:
                        ustatus |= 1L << 32
                    elif rs is 2:
                        ustatus |= 1L << 33

                    gen = i['gender']
                    if 'm' == gen:
                        ustatus |= 1L << 34

                    vt = i['verified_type']
                    if vt is -1:
                        ustatus |= 32L << 35
                    elif vt is 220:
                        ustatus |= 31L << 35
                    elif vt is 200:
                        ustatus |= 30L << 35

                    us = struct.pack(">q", ustatus)
                    usb = buffer(us)
                    m = Mutation(column="relation:%s" % col, value=usb)
                    mutations.append(m)

                    jstop = time()
                    jsonTime = jsonTime + jstop - jstart

                    client.mutateRow("sina_user", row, mutations, None)

                    ind += 1
                except KeyError as e:
                    output.write("##KeyERROR##%s\n" % str(e))
                    continue

            print ind
            output.write("%s%i\n" % ("User数量：", ind))

        except ValueError as e:
            output.write("##ValueERROR##%s\n" % str(e))
            continue

    stop = time()
    output.write("%s%s%s\n" % ("读取文件耗时：", str(fstop-fstart), "秒"))
    output.write("%s%s%s\n" % ("JSON解析耗时：", str(jsonTime), "秒"))
    output.write("%s%s%s\n" % ("总共耗时：", str(stop-start), "秒"))

stoptime = time()
output.write("%s%s\n" % (str(stoptime-startime), "秒"))

transport.close()
output.close()