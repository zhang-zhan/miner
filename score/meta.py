__author__ = 'Peter_Howe<haobibo@gmail.com>'

from collections import OrderedDict
import json,codecs

import dbutil,quiz

def quizs_dump():
    result = OrderedDict()
    cur = dbutil.get_cur()
    cur.execute('SELECT * FROM Quiz ORDER BY QuizId')
    for r in cur:
        qid = r.pop('QuizId')
        result[qid] = r

    with codecs.open('./quiz/meta.data','w',encoding='utf-8') as fp:
        json.dump(result, fp, ensure_ascii=False, encoding='utf-8',indent=1)

def quizs_load():
    with codecs.open('./quiz/meta.data','r',encoding='utf-8') as fp:
        result = json.load(fp, encoding='utf-8')
        return result

quizs = dict()
def get_quiz(quiz_id):
    global quizs
    q = quizs.get(quiz_id,None)
    if q is None:
        q = quiz.Quiz(quiz_id)
        quizs[quiz_id] = q
    return q