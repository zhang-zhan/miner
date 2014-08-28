# -*- coding: utf-8 -*-
import os
from ltp_py import Segmentor as Segmentor_
from ltp_py import Postagger as Postagger_
#from ltp_py import Parser   as Parser_
#from ltp_py import NamedEntityRecognizer as NamedEntityRecognizer_
#from ltp_py import SementicRoleLabeller as SementicRoleLabeller_

config_file = r"D:\Lib\LTP\3.1.0\ltp_data\ltp.cnf"

model = {
    'segmentor-model':None,
    'postagger-model':None,
    'parser-model':None,
    'ner-model':None,
    'srl-data':None
}

def config(file):
    if not os.path.exists(file):
        raise RuntimeError("Config file doesn't exists!")
    base_dir = os.path.abspath(os.path.join(file, os.pardir))
    tmp = {}
    with open(file,'r') as fp:
        for line in fp:
            line = line.strip(' \t\r\n')
            if len(line)<1 or line.startswith('#'): continue
            param = line.split('=')
            if len(param)!=2: continue
            [k,v] = [t.strip(' \t') for t in param]
            tmp[k] = v

        for k in tmp:
            if k not in model: continue
            v = tmp.get(k,None)
            if v is not None:
                 if not os.path.exists(v):
                    v = os.path.join(base_dir, v)
                    if not os.path.exists(v):
                        v = None
            if v is None:
                raise RuntimeError("Model for [%s] is not defined or model file doesn't exist!'" % k)
            model[k] = v

class Segmentor:
    segger = None
    lexion_path = None
    def __init__(self,dic_path=None):
        if dic_path is not None:
            if not os.path.exists(dic_path):
                raise RuntimeError('Given user dictionary [%s] cannot be open!' % dic_path)
            if dic_path == Segmentor.lexion_path:
                if Segmentor.segger is not None:
                    return
            else:
                if Segmentor.segger is not None:
                    Segmentor.segger.release()
                    Segmentor.segger = None

        if Segmentor.segger is None:
            Segmentor.segger = Segmentor_()
            model_ws = model.get('segmentor-model',None)
            if model_ws is None:
                raise RuntimeError('Segmentor Model not set properly!')
            if dic_path is not None:
                Segmentor.segger.load_with_lexicon(model_ws, dic_path)
            else:
                Segmentor.segger.load(model_ws)
        else:
            return

    def release(self):
        if Segmentor.segger is not None: Segmentor.segger.release()

    def getSegger(self):
        if Segmentor.segger is None:
            raise RuntimeError('Please instantiate the Segmentor class first!')
        return Segmentor.segger

class PosTagger:
    tagger = None
    def __init__(self):
        if PosTagger.tagger is None:
            model_pos = model.get('postagger-model',None)
            if model_pos is None:
                raise RuntimeError('POS Tager Model not set properly!')
            PosTagger.tagger = Postagger_()
            PosTagger.tagger.load(model_pos)
        else:
            return

    def getTagger(self):
        if PosTagger.tagger is None:
            raise RuntimeError('Please instantiate the PosTagger class first!')
        return PosTagger.tagger

    def release(self):
        if PosTagger.tagger is not None: PosTagger.tagger.release()

POS ={
    "a"  :	"adjective",
    "b"  :	"other noun-modifier",
    "c"  :	"conjunction",
    "d"  :	"adverb",
    "e"  :	"exclamation",
    "g"  :	"morpheme",
    "h"  :	"prefix",
    "i"  :	"idiom",
    "j"  :	"abbreviation",
    "k"  :	"suffix",
    "m"  :	"number",
    "n"  :	"general noun",
    "nd" :	"direction noun",
    "nh" :	"person name",
    "ni" :	"organization name",
    "nl" :	"location noun",
    "ns" :	"geographical name",
    "nt" :	"temporal noun",
    "nz" :	"other proper noun",
    "o"  :	"onomatopoeia",
    "p"  :	"preposition",
    "q"  :	"quantity",
    "r"  :	"pronoun",
    "u"  :	"auxiliary",
    "v"  :	"verb",
    "wp" :	"punctuation",
    "ws" :	"foreign words",
    "x"  :	"non-lexeme",
    "%"  :   "others"
}

def translatePOS(sPOS):
    return POS.get(sPOS,sPOS)

config(config_file)
segmentor = Segmentor().getSegger()
postagger = PosTagger().getTagger()

def Seg(paragraph, POS=True):
    words = segmentor.segment(paragraph)
    if POS:
        pos = postagger.postag(words)
        r = zip(words,pos)
    else:
        r = words

    for i in r:
        yield i

if __name__ == '__main__':
    p = "Big News: @解放日报 [最右]【呼市铁路局原副局长被判死缓 最头痛藏钱】2013年12月底，呼市铁路局原副局长马俊飞因受贿被判死缓。他说最头痛藏钱，从呼和浩特到北京，马俊飞又是购房又是租房，在挥之不去的恐惧中，人民币8800万、美元419万、欧元30万、港币27万，黄金43.3公斤，逐渐堆满了两所房子…… http://t.cn/8kgR6Yi"
    for t in Seg(p):
        s = '%s\t%s\t%s' % (t[0],t[1],translatePOS(t[1]))
        print(s)