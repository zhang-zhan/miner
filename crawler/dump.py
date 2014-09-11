#-*- encoding=utf-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import codecs,json,time
from dateutil import parser
import util

def dumpStatuses():
    user_paths = util.get_user_path_list('%s')
    for user,path in user_paths.iteritems():
        fname_in = path % 'Status'
        fname_in += '.json'
        fname_profile = path % 'Profile' + '.profile'
        with codecs.open(fname_profile, 'r', 'utf-8-sig') as fp:
            user = json.load(fp,encoding='utf-8')
            uid = user.get('idstr')
            name = user.get('screen_name')

        dump_name = '%s[%s]' % (uid,name) if uid is not None and name is not None else '%s' % user
        fname_out = path.replace(uid,dump_name) % 'Dump/Status'
        fname_out += '.csv'

        with codecs.open(fname_out,'w',encoding='utf-8') as fout:
            fout.write(u'\uFEFF\n')
            with codecs.open(fname_in, 'r', encoding='utf-8') as fin:
                statuses = json.load(fin,encoding='utf-8')
                for s in statuses:
                    createdAt = s.get('created_at')
                    createdAt = parser.parse(createdAt,fuzzy=True)
                    created = time.strftime('%Y/%m/%d %H:%M:%S',createdAt.timetuple())
                    text = s.get('text')
                    mid = s.get('id')
                    n_repost = s.get('reposts_count')
                    n_comment = s.get('comments_count')
                    n_attitude = s.get('attitudes_count')

                    fout.write('%s,%s,%s,%s,%s,%s\n' % (mid,created,n_repost,n_comment,n_attitude,text))


def listFiles():
    d = util.get_user_path_list()
    for name,path in d.iteritems():
        print path+'.txt'

if __name__ == '__main__':
    dumpStatuses()
    #listFiles()
