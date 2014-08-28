# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import codecs
from collections import OrderedDict

from bs4 import BeautifulSoup as bs

import meta


class Question:
    def __init__(self,qid, title=None, tag=None):
        self.qid = qid
        self.title = title
        self.tag = tag
        self.answers = OrderedDict()

    def add_answer(self, aid, score):
        self.answers[aid] = score

    def get_score(self,aid):
        return self.answers.get(aid,0)

class Quiz:
    def __init__(self, quizid):
        self.quiz_id = quizid

        #Setting XML File
        quizs = meta.quizs_load()
        quiz = quizs.get(quizid)
        self.xml = quiz.get('XmlPath')

        #Setting questions
        self.questions = OrderedDict()
        fp = codecs.open(self.xml,'r',encoding='utf-8')
        x = bs(fp)
        x = x.find_all('question')
        for q in x:
            qid = q['qid']
            title = q.title.string
            tag = q.get('tag')
            _q = Question(qid,title,tag)

            for a in  q.children:
                if a.name is None or a.name!='answer':continue
                aid = a['aid']
                score = a['score']
                _q.add_answer(aid,score)

            self.questions[qid] = _q


    def parse(self, s, col_name=None):
        result = OrderedDict()

        ll = s.split('#')
        for l in ll:
            if len(l)==0: continue
            a = l.split('@')
            key = a[0]
            value = a[1].strip(' \t\r\n[]')
            if col_name is not None:
                key = col_name if key=='_def' else"%s_%s" % (col_name, key)

            result[key] = value
        return result

    def score(self, s, col_name=None):
        '''Given an answer str s, parse the string and calculate the score according to xml questionnaire file.'''
        dimensions = dict()

        ans = self.parse(s)
        for qid,aid in ans.iteritems():

            _q = self.questions.get(qid)
            if _q is None: continue

            tag = _q.tag
            score = _q.get_score(aid)

            s_old = dimensions.get(tag, 0)
            dimensions[tag] = s_old + int(score)

        if col_name is not None:
            r_dimensions = OrderedDict()
            for tag,score in dimensions.iteritems():
                key = col_name if tag is None or tag=='_def' else"%s_%s" % (col_name, tag)
                r_dimensions[key] = score

            dimensions = r_dimensions

        return dimensions

if __name__ == '__main__':
    pass
    #q = Quiz('')
    #q.parse()