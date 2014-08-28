__author__ = 'jiaodongdong'
#coding:utf-8
import struct
import codecs
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

#output = open("C:/Share/LoadDataConf/user.txt", "a")#存放日志
desd = "C:/Share/LoadDataConf/"
diri = 'Users'
diri2 = 'user_in'

diri3 = 'status_in'

dirf = u'Z:/2013Dec-ImportData'
fileList = os.listdir(dirf)

c = 0

for ind in range(0, 24):
    dd = desd + diri3 + str(ind) + '.txt'
    inputf = open(dd, 'r')
    host = inputf.readline().strip('\n')
    port = inputf.readline().strip('\n')

    dd2 = desd + diri2 + str(ind) + '.txt'
    output = open(dd2, 'a')
    output.write("%s\n" % str(host))
    output.write("%s\n" % str(port))
    inputf.close()
    output.close()

for f in fileList:
    dirf2 = dirf + '/' + f
    fileList2 = os.listdir(dirf2)
    for f2 in fileList2:
        if str(f2) == 'SinaNormalRobot':
            dirf3 = dirf2 + '/'+f2
            fileList3 = os.listdir(dirf3)
            for f3 in fileList3:
                if str(f3) == diri:
                    dirf4 = dirf3 + '/'+f3
                    fileList4 = os.listdir(dirf4)
                    for f4 in fileList4:
                        dirf5 = dirf4 + '/'+f4

                        index = int(c / 18060)
                        dd = desd + diri2 + str(index) + '.txt'
                        output = open(dd, 'a')
                        output.write("%s\n" % str(dirf5))
                        output.close()

                        c += 1

print c
