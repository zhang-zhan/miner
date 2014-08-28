# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

from collections import OrderedDict
from datetime import datetime
import dbutil,meta

dimensions = OrderedDict()
users = dict()

quiz_with_answer = ['Q2_Demographic']

def get_exp_fills(ExpId):
    cur = dbutil.get_cur()
    cur.execute('CALL P_GetExpFills(%s,null,null)' % ExpId)
    for r in cur:
        sina_uid = r['SiteUid']
        quiz_id = r['QuizId']
        costseconds = r['CostSeconds']
        filltime = r['LastFill']
        answer = r['Answer']
        score = r['Score']

        quiz = meta.get_quiz(quiz_id)
        ss = quiz.score(answer,col_name=quiz_id)

        u = users.get(sina_uid)
        if u is None:
            u = OrderedDict()
        u.update(ss)
        for s in ss:
            dimensions[s] = 0

        if quiz_id in quiz_with_answer:
            answers = quiz.parse(answer,quiz_id)
            u.update(answers)
            for a in answers:
                dimensions[a] = 0

        dim_cost_seconds = '%s_CostSeconds' % quiz_id
        dim_fill_time = '%s_FillTime' % quiz_id

        u[dim_cost_seconds] = costseconds
        u[dim_fill_time] = datetime.strftime(filltime,'%Y/%m/%d %H:%M:%S')

        dimensions[dim_cost_seconds] = 0
        dimensions[dim_fill_time] = 0

        users[sina_uid] = u


if __name__ == '__main__':
    get_exp_fills(2)

    header = "SinaUid\t"
    for dim in dimensions:
        header += "%s\t" % dim
    print header

    for u,scores in users.iteritems():
        line = '%s\t' % u
        for dim in dimensions:
            line += '%s\t' % scores[dim]

        print line