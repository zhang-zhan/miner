# -*- encoding=utf-8 -*-
__author__ = 'Peter'

import codecs,json,re,datetime
from collections import OrderedDict as dict
from dateutil import parser

import util
import nlpir
import numpy

screen_names = util.get_user_path_list('%s')
re_exp = re.compile(r'\[(\S+?)\]')
re_grp = re.compile(r'Weibo\/(\w+)\/')
neg_exp = util.get_lines('./Exps-Neg.lst')


# 第一人称复数 http://baike.baidu.com/view/1569657.htm
set_We = set(['我们','大家','咱们','咱们','俺们'])

# 第一人称单数
set_I = set(['我','俺'])

textLen = []

def extractProfile(fname):
    f = dict()
    #f['Group'] = re.findall(re_grp,fname)[0]

    with codecs.open(fname,'r',encoding='utf-8') as uf:
        u = json.load(uf)

        f['UID'] = str(u['id'])
        f['Nick'] = u['screen_name']
        f['性别'] = u['gender']
        f['所在地'] = u['location']
        f['允许所有人发送私信'] = '1' if u['allow_all_act_msg'] else '0'
        f['允许所有人评论'] = '1' if u['allow_all_comment'] else '0'
        f['有自定义头像'] = '1' if '180/0/' in u['avatar_large'] else '0'
        f['互粉数/粉丝数'] = str(1.0 * u['bi_followers_count'] / u['followers_count']) if u['followers_count']>0 else 'DIV#0'
        f['互粉数/关注数'] = str(1.0 * u['bi_followers_count'] / u['friends_count']) if u['friends_count']>0 else 'DIV#0'
        f['互粉数'] = str(u['bi_followers_count'])
        f['开博日期'] = str( parser.parse(u['created_at'],fuzzy=True).date() )
        f['自我描述长度'] = str( len( u['description'])  )
        f['自我描述中含“我”'] = '1' if u'我' in u['description'] else '0'
        f['个性域名'] = u['domain']
        f['域名长度'] = str( len( u['domain'] ))
        f['域名中含数字'] = '1' if len([val for val in u['domain'] if val in '0123456789'])>0 else '0'
        f['微博数'] = str(u['statuses_count'])
        f['收藏数'] = str(u['favourites_count'])
        f['粉丝数'] = str( u['followers_count'] )
        f['关注数'] = str( u['friends_count'] )
        f['开启地理定位'] = '1' if u['geo_enabled'] else '0'
        f['用户个人网站URL含域名'] = '1' if u['domain'] in u['url'] else '0'
        f['昵称长度'] = str( len( u['screen_name'] ) )
        f['用户有个人网站URL'] = '1' if u['url'] is not None else '0'
        f['是否认证'] = '1' if u['verified'] else '0'
        f['认证原因长度'] = str( len ( u['verified_reason'] ) )
        f['认证类别'] = str(u['verified_type'])
        f['省/市ID'] = u['province']
        f['市/区ID'] = u['city']
    return f

def extractWeibo(fname):
    nStatuses = 0
    nOriginal = 0
    nOrigStatusWithPics = 0
    nContainsUrl = 0
    nContainsMention = 0
    nContainsWe = 0
    nContainsI = 0
    nComposeLate = 0
    nNegExps = 0

    nTextLength = []

    minCreatedAt = parser.parse('Dec 31 23:59:59 +0800 2099',fuzzy=True)
    maxCreatedAt = parser.parse('Jan 01 00:00:01 +0800 1970',fuzzy=True)

    try:
        f = codecs.open(fname,'r',encoding='utf-8')

        statuses = json.load(f,encoding='utf-8')
        nStatuses += len(statuses)

        for s in statuses:
            text = s['text']
            l = len(text)
            nTextLength.append( l )

            isOriginal = 1 if s.get('retweeted_status',None) is None else 0
            nOriginal += isOriginal

            containsPic = s.get('pic_ids',None) is not None \
                or s.get('pic_urls',None) is not None
            nOrigStatusWithPics += 1 if isOriginal>0 and containsPic else 0

            containsUrl = 'http://t.cn/' in text
            nContainsUrl += 1 if containsUrl else 0

            containsMention = '@' in text
            nContainsMention += containsMention

            if l==0:
                words = []
            else:
                t = text.encode('UTF-8')
                words = nlpir.Seg(t)

            for i in words:
                word = i[0]
                if word in set_I : nContainsI += 1
                if word in set_We : nContainsWe += 1

            createdAt = parser.parse(s['created_at'],fuzzy=True)

            if createdAt < minCreatedAt: minCreatedAt = createdAt
            if createdAt > maxCreatedAt: maxCreatedAt = createdAt

            createdHour = createdAt.hour
            if not ( createdHour > 6 and createdHour < 22):
                nComposeLate += 1

            exps = re.findall(re_exp,text)
            for exp in exps:
                if exp in neg_exp:
                    nNegExps += 1

        f.close()
        f = dict()
        f['公开微博总数'] = nStatuses
        f['原创微博数'] = nOriginal
        f['含图片原创微博数'] = nOrigStatusWithPics
        f['含URL微博数'] = nContainsUrl
        f['含@的微博数'] = nContainsMention
        f['微博中第一人称复数使用次数'] = nContainsWe
        f['微博中第一人称单数使用次数'] = nContainsI
        f['夜间时段发微博数'] = nComposeLate
        f['含消极表情总数'] = nNegExps
        f['公开微博字数平均值'] = numpy.mean(nTextLength) if len(nTextLength)>0 else 'N/A'
        f['公开微博字数STD'] = numpy.std(nTextLength) if len(nTextLength)>0 else 'N/A'
        f['公开微博字数MAX'] = numpy.max(nTextLength) if len(nTextLength)>0 else 'N/A'
        f['公开微博字数MIN'] = numpy.min(nTextLength) if len(nTextLength)>0 else 'N/A'
        f['公开微博字数MEDIAN'] = numpy.median(nTextLength) if len(nTextLength)>0 else 'N/A'
        f['最早一条微博发布时间'] = minCreatedAt.date()
        f['最后一条微博发布时间'] = maxCreatedAt.date()

        for k,v in f.iteritems():f[k] = str(v)

        global textLen
        textLen.extend(nTextLength)

        return f

    except IOError as e:
        return {}

def extractComments(fname):
    pass

def extract():
    for screen_name,path in screen_names.iteritems():
        f1 = extractProfile( (path%'Profile') + '.profile')
        f2 = extractWeibo( (path%'Status') + '.json')
        #extractComments(path)

        f1.update(f2)

        line=''
        for k,v in f1.iteritems():
            line += v + '\t'
        print line

    line = ''
    for i in f1.keys():
        line += i + '\t'
    print(line)

if __name__ == '__main__':
    extract()

    global textLen
    print numpy.mean(textLen)
    print numpy.std(textLen)
    print numpy.min(textLen)
    print numpy.max(textLen)
    print numpy.median(textLen)