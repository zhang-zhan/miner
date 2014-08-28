# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import os,codecs,re,collections

from maps import SetMultimap

#字典命名规范：[字典格式：dic/lst/sym].[字典名称].[其他说明]
regex_dic = "^(\w+).(\w+)([\.|\w]*)"

terms = SetMultimap(ordered=True)

path = os.path.dirname(os.path.realpath(__file__))
dic_dir = path.replace('\\','/')
if not dic_dir.endswith('/'): dic_dir += '/'
dic_dir += 'dic/'

debug = False

def load_map(map_file=dic_dir+"/map.textmind.ALL", result_dic = None):
    if result_dic is None:
        result_dic = collections.OrderedDict()

    with codecs.open(map_file, 'r', encoding='utf-8-sig') as fp:
        for line in fp:
            line = line.strip(' \t\r\n')
            if len(line)<1 or line[0] == '%': continue  #以%开头的行作为字典文件的注释
            if len(line)<1:continue

            (i, tag) = line.split('\t')
            result_dic[tag.lower()] = int(i)

    return result_dic

def load_code_map(map_file="./dic/map.textmind.ALL"):
    result = {}
    with codecs.open(map_file, 'r', encoding='utf-8-sig') as fp:
        for line in fp:
            line = line.strip(' \t\r\n')
            if len(line)<1 or line[0] == '%': continue  #以%开头的行作为字典文件的注释
            if len(line)<1:continue

            (i, tag) = line.split('\t')
            result[i] = tag.lower()
    return result

def load_dic_terms(file_path, result_dic=None, prefix=None, tag_delimiter='\t', code_map=None):
    """
     Load a dictionary to specified dictionary variable and return the number of terms and tags as tuple loaded.
     If result_dic is not specified, terms will be loaded to the global variable: terms.
    """
    n_term = 0
    n_tag = 0
    if result_dic == None: result_dic = terms
    with codecs.open(file_path, 'r', encoding='utf-8-sig') as fp:
        for line in fp:
            line = line.strip(' \t\r\n')
            if len(line)<1 or line[0] == '%': continue  #以%开头的行作为字典文件的注释

            crumbs = line.split('\t')
            term = crumbs.pop(0)

            for crumb in crumbs:
                t_crumbs = crumb.split(tag_delimiter)
                for t in t_crumbs:
                    if code_map is not None: t = code_map.get(t)
                    if prefix is not None: t = '%s/%s' % (prefix,t)
                    result_dic[term].add(t)
                    n_tag += 1

            n_term += 1

    if debug:
        info = "%6d terms with %6d tags loaded from dictionary [%s]." % (n_term, n_tag,file_path)
        print info
    return (n_term, n_tag)

def load_dic_terms_as_set(file_path):
    """tag information will be ignored"""
    result = set()
    with codecs.open(file_path, 'r', encoding='utf-8-sig') as fp:
        for line in fp:
            line = line.strip(' \t\r\n')
            if len(line)<1 or line[0] == '%': continue  #以%开头的行作为字典文件的注释

            crumbs = line.split('\t')
            term = crumbs.pop(0)

            result.add(term)

    return result

def load_lst_terms(file_path, tag_name, result_dic=None, prefix=None):
    """
    Load a dictionary to specified dictionary variable with given tag_name,
    and return the number of terms and tags as tuple loaded.
    If result_dic is not specified, terms will be loaded to the global variable: terms.
    """
    n_term = 0
    if result_dic == None: result_dic = terms
    with codecs.open(file_path, 'r', encoding='utf-8-sig') as fp:
        for line in fp:
            line = line.strip(' \t\r\n')
            if len(line)<1 or line[0] == '%': continue  #以%开头的行作为字典文件的注释

            t = '%s/%s' % (prefix,t) if prefix is not None else tag_name
            result_dic[line].add(t)
            n_term += 1

    if debug:
        info = "%6d terms with %6d tags loaded from dictionary [%s]." % (n_term, 1, file_path)
        print info
    return (n_term, 1)

def load_all_dic():
    n_dic = 0
    n_term = 0
    n_tag = 0

    all_files = os.listdir(dic_dir)
    for f in all_files:
        dic_path = dic_dir + f
        if os.path.isdir(dic_path): continue

        r = re.findall(regex_dic,f)

        if len(r)<1: continue
        else: (_format, _name, _desc) = r[0]

        if _format in [ 'dic', 'sym']:
            (t_term, t_tag) = load_dic_terms(dic_path,prefix=_name)
        elif _format == 'lst':
            (t_term, t_tag) = load_lst_terms(dic_path,_desc,prefix=_name)
        elif _format == 'ptn':
            (t_term, t_tag) = (0,0)    #目前不对通配符做处理
        else:
            continue

        n_term += t_term
        n_tag += t_tag
        n_dic += 1

    if debug:
        info = "%6d terms with %6d tags loaded from %s dictionary(ies)." % (n_term, n_tag,n_dic)
        print info

def aggregate_tags(terms = terms, enableWarnning=False):
    """
    return a map from tags without suffix to tags with suffix, where the key is all lower case,
    and the map is ordered according to output order.
    """
    ordered_tags = load_map()

    tmp_tags = collections.OrderedDict()    #All keys to lowe cases
    for k in ordered_tags.keys():
        tag = k.lower()
        tmp_tags[tag] = k

    for term,tags in terms.iteritems():
        for tag in tags:
            try:
                ind = tag.rindex('/')
                tmp = tag[ind+1:]
            except ValueError as e:
                tmp = tag

            tmp = tmp.lower()
            if tmp in tmp_tags:
                tmp_tags[tmp] = tag
            else:
                if enableWarnning:
                    print('Unknown tag ignored:[%s] for term [%s].' %  (tag,term) )

    return tmp_tags

def dump_dic(output_path, dic=terms):
    if isinstance(dic,SetMultimap): dic = dic._dict
    with codecs.open(output_path, 'w', encoding='utf-8-sig') as fp:
        for term,tags in dic.iteritems():
            fp.write(term)
            for tag in tags:
                fp.write('\t%s' % tag)
            fp.write('\n')

if __name__ == "__main__":
    debug=True
    load_all_dic()
    dump_dic('D:/dic.txt')
    tags = aggregate_tags()
    for a,b in tags.iteritems():
        print '%s\t%s' % (a,b)