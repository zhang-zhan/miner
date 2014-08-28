#encoding=utf-8
__author__ = 'jiaodongdong'


import os
import json

fileBase = u'Z:\Details1\微博爬虫发布版—新4.0 —for—detail—01\weibo_datas\SinaDetailRobot'

def importUsers(folder):
    curDir = os.path.join(fileBase, folder)
    filesList = os.listdir(curDir)

    for ftmp in filesList:
        f = os.path.join(curDir, ftmp)
        with open(f ,'rt') as jsonFile:
            t = jsonFile.read()
            users = json.loads(t)
            print( len(users) )
            for u in users:
                try:
                    n1 = u['screen_name']
                    n2 = u['name']
                    print(n1==n2)
                except KeyError as e:
                    print(e)

def importStatus(folder):
    curDir = os.path.join(fileBase, folder)
    print('curDir:' + curDir)
    filesList = os.listdir(curDir)

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
                print(s['in_reply_to_user_id'])


#importUsers(u'Users')
#importUsers(u'RelationshipUsers')
importStatus(u'Statuses')