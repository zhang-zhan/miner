# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import codecs,json,os

file = r"J:\Compare-New\Compare.xlsx"
dir_profile = r"J:/Compare-New/Profile/"
dir_status = r"J:/Compare-New/Profile/"

def getUAttr(uid,attr):
    fname = "%s%s.profile" % (dir_profile,uid)
    if not os.path.exists(fname):
        return "No User in [%s]" % fname

    attrs = attr.split('/')
    with codecs.open(fname,'r',encoding='utf-8') as fp:
        profile = json.load(fp,encoding='utf-8')
        t = profile
        for a in attrs:
            if t is not None:
                t = t.get(a,None)
    return "#"+str(t) if t is not None else 'N/A'