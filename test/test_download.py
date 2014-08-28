# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import json
from weibo.sina import APIClient
from weibo.token import getToken

from weibo import Status
from hbase import gateway

uname = 'd3a907fbea42783d@sina.com'
passwd = 'd3a907fbea42783d'

access_token = getToken(uname,passwd) #'2.00jAczuCfj3PXC883178e9a0zwIHRD'
print(access_token)

APP_KEY = 'APP_KEY'            # app key
APP_SECRET = 'YOUR_APP_SECRET'      # app secret
CALLBACK_URL = 'YOUR_CALLBACK_URL'  # callback url

client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
client.access_token = access_token

statuses = client.statuses.public_timeline.get(count=200)

statuses = statuses.get('statuses')
for s in statuses:

    r_status = Status()
    r_status.load(s)

    batch = r_status.get_batches()
    gateway.applyBatch(batch)





#friends = client.friendships.friends.get(screen_name='Peter_Howe',trim_status=1,count=200,page=1)
#friends = client.friendships.followers.get(screen_name='Peter_Howe',trim_status=1,count=200,page=1)
#friends = client.friendships.friends.bilateral.get(uid=1096081744,trim_status=1,count=200,page=1)
#friends = friends['users']
#print len(friends)
#f = friends[11]
#ff = json.dumps(friends,ensure_ascii=False,indent=2,sort_keys=True)
#print ff

#tags = client.tags.get(uid=2721210291)
#f = json.dumps(tags,ensure_ascii=False,indent=1,sort_keys=True)
#print f