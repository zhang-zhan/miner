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
    'status': ['idstr', 'text', 'created_at', 'reposts_count', 'comments_count', 'attitudes_count',
               'source', 'truncated']
}

repos = {
    'repost': ['text', 'created_at', 'reposts_count', 'comments_count', 'attitudes_count', 'source',
               'truncated']
}

output = open("C:/Share/LoadDataConf/status.log", "a")#存放日志


curList = []
input = open("C:/Share/LoadDataConf/status_in.txt", "r")#配置文件第一行是host第二行是port剩余行是输入文件件
host = input.readline().strip('\n')
port = input.readline().strip('\n')
while 1:
    curDirt = input.readline().strip('\n').decode("utf-8")
    if not curDirt:
        break
    curList.append(curDirt)
input.close()

outputerror = open("C:/Share/LoadDataConf/status_in_error.txt", "a")
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
    start = time.time()
    output.write("%s\n" % f.encode("utf-8"))
    jsonTime = float(0)
    fstart = time.time()
    with open(f, 'rt') as jsonFile:
        try:
            t = jsonFile.read()
            users = json.loads(t)
            #print( len(users) )
            ind = 0
            fstop = time.time()
            for i in users:
                jstart = time.time() #count

                ustatus = 0L
                ustatus = ustatus + mtime

                u = User(i)
                sid = i['id']
                user = u.__getattr__('user')
                if user is None:
                    continue
                uid = user['id']

                key = struct.pack('<qq', uid, sid)
                row = buffer(key)

                uk = struct.pack('<q', uid)
                urow = buffer(uk)

                usk = struct.pack('>q', uid)
                uid2 = buffer(usk)

                mutations = []
                mutations_user = []
                m = Mutation(column="status:uid", value=uid2)
                mutations.append(m)

                for f, cc in attrs.iteritems():
                    for c in cc:
                        v = u.__getattr__(c)
                        #print(type(v))
                        if v is None:
                            continue
                        if c is 'created_at':
                            m = Mutation(column="%s:%s" % (f, 'c_at_or'), value=v)
                            mutations.append(m)
                            sd = date2unix(v)
                            ke = struct.pack('>i', sd)
                            ro = buffer(ke)
                            m = Mutation(column="%s:%s" % (f, c), value=ro)
                            mutations.append(m)
                        elif c is 'reposts_count':
                            m = Mutation(column="%s:%s" % (f, c), value=v)
                            mutations.append(m)
                            ir = struct.unpack(">i", v)
                            if ir[0] is 0:
                                ustatus |= 1L << 35
                        elif c is 'comments_count':
                            m = Mutation(column="%s:%s" % (f, c), value=v)
                            mutations.append(m)
                            ir = struct.unpack(">i", v)
                            if ir[0] is 0:
                                ustatus |= 1L << 36
                        elif c is 'attitudes_count':
                            m = Mutation(column="%s:%s" % (f, c), value=v)
                            mutations.append(m)
                            ir = struct.unpack(">i", v)
                            if ir[0] is 0:
                                ustatus |= 1L << 37
                        else:
                            m = Mutation(column="%s:%s" % (f, c), value=v)
                            mutations.append(m)
                #print(mutations)
                #break

                ge = u.__getattr__('geo')
                if ge is not None:
                    ustatus |= 1L << 33
                    g = str(ge)
                    m = Mutation(column="status:geo", value=g)
                    mutations.append(m)

                pic = u.__getattr__('pic_urls')
                if pic is not None:
                    ustatus |= 1L << 34
                    p = str(pic)
                    m = Mutation(column="status:pic_urls", value=p)
                    mutations.append(m)

                rep = u.__getattr__('retweeted_status')
                if rep is not None:

                    rsid = rep['id']
                    rk = struct.pack('>q', rsid)
                    rid = buffer(rk)
                    m = Mutation(column="status:r_id", value=rid)
                    mutations.append(m)

                    m = Mutation(column="repost:id", value=rid)
                    mutations.append(m)

                    repo = User(rep)
                    for re, col in repos.iteritems():
                        for cl in col:
                            va = repo.__getattr__(cl)
                            #print(type(va))
                            if va is None:
                                continue
                            if cl is 'created_at':
                                m = Mutation(column="%s:%s" % (re, 'c_at_or'), value=va)
                                mutations.append(m)
                                sd = date2unix(va)
                                ke = struct.pack('>i', sd)
                                ro = buffer(ke)
                                m = Mutation(column="%s:%s" % (re, cl), value=ro)
                                mutations.append(m)
                            else:
                                m = Mutation(column="%s:%s" % (re, cl), value=va)
                                mutations.append(m)

                    ruser = repo.__getattr__('user')
                    if ruser is not None:
                        ruid = ruser['id']
                        rs = struct.pack(">q", ruid)
                        ruid2 = buffer(rs)
                        m = Mutation(column="repost:uid", value=ruid2)
                        mutations.append(m)

                    ge = repo.__getattr__('geo')
                    if ge is not None:
                        g = str(ge)
                        m = Mutation(column="repost:geo", value=g)
                        mutations.append(m)

                    pic = repo.__getattr__('pic_urls')
                    if pic is not None:
                        p = str(pic)
                        m = Mutation(column="repost:pic_urls", value=p)
                        mutations.append(m)
                else:
                    ustatus |= 1L << 32
                    rid = 0L
                    rp = struct.pack(">q", rid)
                    ridb = buffer(rp)
                    m = Mutation(column="status:r_id", value=ridb)
                    mutations.append(m)

                us = struct.pack(">q", ustatus)
                ub = buffer(us)
                mu = Mutation(column="status:%s" % row, value=ub)
                mutations_user.append(mu)

                jstop = time.time()
                jsonTime = jsonTime + jstop - jstart

                client.mutateRow("sina_user", urow, mutations_user, None)

                client.mutateRow('sina_status', row, mutations, None)
                #break
                ind += 1
                #if ind > 100:
                    #break
            print ind
            output.write("%s%i\n" % ("微博数量：", ind))
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

    stop = time.time()
    output.write("%s%s%s\n" % ("读取文件耗时：", str(fstop-fstart), "秒"))
    output.write("%s%s%s\n" % ("JSON解析耗时：", str(jsonTime), "秒"))
    output.write("%s%s%s\n" % ("总共耗时：", str(stop-start), "秒"))
    #break

stoptime = time.time()
output.write("%s%s\n" % (str(stoptime-startime), "秒"))

transport.close()
output.close()

