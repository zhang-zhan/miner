# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

from collections import defaultdict, OrderedDict
from maps import SetMultimap
from filter import Filter
from helper import load_dic_terms, load_dic_terms_as_set, dump_dic,load_map, load_code_map
from helper import dic_dir

def route_dic(terms, temp_original_liwc = None, temp_tags = None):
    route_dics = defaultdict(SetMultimap)

    f = Filter(
        term_in_collection = temp_original_liwc,
        tag_in_collection = temp_tags
    )

    for term, tags in terms._dict.iteritems():
        for tag in tags:
            code = f.route(term, tag)
            d = route_dics[code]
            d[term].add(tag)

    for n,dic in route_dics.iteritems():
        dump_dic('%s/C%d.txt' % (dic_dir,n), dic=dic)

if __name__ == '__main__':

    _temp_tags = set(['Psychology', 'Love', 'tPast', 'tNow', 'tFuture'])
    tag_map = OrderedDict()
    load_map(result_dic=tag_map)
    temp_tags = set([ i for i,tag in tag_map.iteritems() if tag in _temp_tags  ])

    #temp_original_liwc = load_dic_terms_as_set(dic_dir+'')

    terms = SetMultimap()
    code_map = load_code_map()
    load_dic_terms(dic_dir + 'bak.dic.textmind.TCLIWC',result_dic = terms, code_map=code_map)
    route_dic(terms, temp_tags = temp_tags)