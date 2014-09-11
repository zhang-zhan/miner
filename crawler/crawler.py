# -*- encoding=utf-8 -*-
__author__ = 'Peter Howe(haobibo@gmail.com)'

import math,os,codecs,time
from weibo.token import getToken
from weibo.sina import *

uname = 'd3a907fbea42783d@sina.com'
passwd = 'd3a907fbea42783d'

access_token = getToken(uname,passwd) #'2.00jAczuCfj3PXC883178e9a0zwIHRD'
print(access_token)

APP_KEY = '2083434837'            # app key
APP_SECRET = 'YOUR_APP_SECRET'      # app secret
CALLBACK_URL = 'YOUR_CALLBACK_URL'  # callback url

base_dir = 'J:/Compare-New/'
debug_enable = True
download_fewer_statuses = False
sleep_span = 0.4

schema='https' if debug_enable else 'http'
domain = 'api.weibo.com' if debug_enable else 'i2.api.weibo.com'

client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL,schema=schema,domain=domain)
client.access_token = access_token

def get_all_statuses(**kwargs):
    try:
        u = client.users.show.get(**kwargs)
    except Exception as e:
        print(e.message)
        return []

    nStatus = int( u['statuses_count'] )

    per_page = 200.0
    nPages = math.ceil( nStatus / per_page)
    nPages = int( nPages )

    ss = []
    for i in range(1,nPages+1):
        kwargs['count'] = int(per_page)
        kwargs['page'] = i
        if 'screen_name' in kwargs:
                kwargs['screen_names'] = kwargs.pop('screen_name',None)

        if download_fewer_statuses:
            if 'uid' in kwargs:
                kwargs['uids'] = kwargs.pop('uid',None)
            s = client.statuses.user_timeline.get(**kwargs)
        else:
            s = client.statuses.user_timeline.get(**kwargs)

        statuses = s['statuses']
        ss.extend(statuses)

    return ss

def get_commnets_by_status(id, comments_count):
    per_page = 200.0
    nPages = math.ceil( comments_count / per_page)
    nPages = int( nPages )

    cc = []
    min_page = min(nPages,0)
    for i in range(nPages,min_page, -1):
        c = None
        max_try = 3
        while max_try>0:
            try:
                c = client.comments.show.get(id=id, count=200, page=i)
                break
            except:
                max_try -= 1
                continue

        if c is None or len(c)==0:
            continue

        comments = c.get('comments',[])
        for t in comments:
            try:
                t.pop('status')
            except Exception as e:
                print e #pass

            cc.append(t)
    return cc


def download_user_statuses_comments(uid_tasks):
    for uid, path in uid_tasks.iteritems():
        print('Downloading user status of [%s].' % uid)
        status_fpath = '%s/Status/%s.json' % (base_dir, uid)
        if not os.path.exists(status_fpath):
            print('Downloading info of user: %s ...' % uid)
            try:
                statuses = get_all_statuses(uid=uid)
                with codecs.open((path % 'Status')+'.json', 'w', encoding='utf-8') as f:
                    json.dump(statuses,f,ensure_ascii=False)
            except APIError as e:
                print uid, e
            except Exception as e:
                print uid, e
        else:
            with codecs.open(status_fpath,'r','utf-8-sig') as fp_status:
               statuses = json.load(fp_status,encoding='utf-8')

        #download status comments
        cmt_folder = '%s/Comments/%s/' % (base_dir, uid)
        if os.path.exists(cmt_folder + 'done'):
            continue

        try: os.makedirs(cmt_folder)
        except: pass

        for status in statuses:
            #time.sleep(sleep_span)

            cmts_count = int( status['comments_count'] )
            if cmts_count < 1:continue

            mid = str( status['id'] )

            cmt_fpath = cmt_folder + '%s.json' % mid
            if os.path.exists(cmt_fpath):
                continue

            comments = get_commnets_by_status(mid,cmts_count)
            cmt_len = len(comments)
            print('  Download Comment [%s].[%s]->[%d]' % (uid,mid,cmt_len))
            if cmt_len < 1:continue

            with codecs.open(cmt_fpath,'w',encoding='utf-8') as f:
                json.dump(comments, f, ensure_ascii=False)

        with codecs.open(cmt_folder + 'done', 'w', encoding='utf-8') as fp:
            fp.write('done')



def download_user_profile(uid_tasks):
    for uid, path in uid_tasks.iteritems():
        if os.path.exists('%s/Profile/%s.profile' % (base_dir, uid)):
            continue

        try:
            u = client.users.show.get(uid=uid)
            print '%s\t%s\t%s\t%s' % (u['id'], u['gender'], u['screen_name'],u['statuses_count'])
            with codecs.open( (path % 'Profile') + '.profile','w',encoding='utf-8') as f:
                json.dump(u,f,ensure_ascii=False)
        except APIError as e1:
            print uid, e1.message
        except UnicodeEncodeError as e2:
            print uid,e2
            json.dump(u,f,ensure_ascii=True)

def get_user_profile(**kwargs):
    lst = key = None
    try:
        lst = kwargs.pop('screen_name')
        key = 'screen_name'
    except:
        pass

    if lst==None:
        try:
            lst = kwargs.pop('uid')
            key = 'uid'
        except:
            pass

    if lst is None:
        raise ValueError('User list shall not be None!')

    profiles = []
    for user in lst:
        t = {key:user}

        try:
            u = client.users.show.get(**t)
            print '%s\t%s\t%s\t%s' % (u['id'], u['gender'], u['screen_name'],u['statuses_count'])
            profiles.append(u)
        except APIError as e:
            print e

    return profiles

def run():
    import util

    #uids = util.get_lines(base_dir + 'TaskList.txt')
    #param = {'uid':uids}
    #users = get_user_profile(**param)
    #with codecs.open(base_dir + 'UserInfo.txt', 'w',encoding='utf-8') as fp:
    #    json.dump(users,fp,ensure_ascii=False,encoding='utf-8')

    uid_tasks = util.get_user_path_list('%s')
    download_user_profile(uid_tasks)
    download_user_statuses_comments(uid_tasks)

if __name__ == '__main__':
    run()