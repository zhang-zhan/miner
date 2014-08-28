#encoding=utf-8
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import os
import json
from pymongo import MongoClient



mongoURL = 'mongodb://192.168.21.224:27017/'
fileBase = u'E:/数据导入/2000人新数据/weibo_datas/SinaNormalRobot/'


client = MongoClient(mongoURL)
db = client['weibo_2K']

def importUsers(folder):
    curDir = os.path.join(fileBase, folder)
    filesList = os.listdir(curDir)

    dbUsers = db.users
    dbUsers.ensure_index("id",unique=True)

    for ftmp in filesList:
        f = os.path.join(curDir, ftmp)
        with open(f ,'rt') as jsonFile:
            t = jsonFile.read()
            users = json.loads(t)

            for u in users:
                try:
                     dbUsers.insert(u)
                except:
                    print('duplicate key: %d' % u['id'])

def importStatus(folder):
    curDir = os.path.join(fileBase, folder)
    print('curDir:' + curDir)
    filesList = os.listdir(curDir)

    dbStatuses = db.statuses
    dbStatuses.ensure_index("id",unique=True)

    for ftmp in filesList:
        f = os.path.join(curDir, ftmp)
        print('ftmp file:' + f)

        with open(f ,'rt') as jsonFile:
            print('ready to read file : '+ f)
            t = jsonFile.read()

            print('ready to parse file : '+ f)
            statuses = json.loads(t)

            print('ready to dump file : '+ f)
            for s in statuses:
                #print(s[id])
                try:
                    dbStatuses.insert(s)
                except:
                    print('duplicate key: %d' % s['id'])

importUsers(u'Users')
importUsers(u'RelationshipUsers')
#importStatus(u'Statuses')