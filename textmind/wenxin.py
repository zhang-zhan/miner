# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import codecs,re
import nlpir
import helper
from result import Result
sentence_separator = [',' ,'。', '?', '？', '!', '！', ';', '；'] #句号 问号 叹号 分号
sentence_separator = set([i.decode('utf-8') for i in sentence_separator])

rx_latin = re.compile("[^\W\d_]+", re.UNICODE)
rx_numeral = re.compile(r"([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)",re.UNICODE)
rx_url = re.compile(r"((ht|f)tp(s?)\:\/\/[0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*(:(0-9)*)*(\/?)([a-zA-Z0-9\-‌​\.\?\,\'\/\\\+&amp;%\$#_]*)?)", re.UNICODE)
rx_emotion = re.compile(r"(\[(.{1,16}?)\])", re.UNICODE)
rx_at_mention = re.compile(r"@[\u4e00-\u9fa5a-zA-Z0-9_-]{4,30} ", re.UNICODE)
rx_hashtag = re.compile(r"#[^#]+#", re.UNICODE)

def is_sentence_separator(term):  return term in sentence_separator
def is_latin(term):               return rx_latin.match(term) is not None
def find_numeral(istr):           return [t[0] for t in rx_numeral.findall(istr)]
def find_url(istr):               return [t[0] for t in rx_url.findall(istr)]
def find_emotions(istr):          return [t[0] for t in rx_emotion.findall(istr)]
def find_at_mention(istr):        return [t[0] for t in rx_at_mention.findall(istr)]
def find_hashtag(istr):           return [t[0] for t in rx_hashtag.findall(istr)]

def get_term_tags(term):
    return TextMind._dic.get(term,[])

class TextMind:
    def __init__(self, enablePOS = False):
        self.enablePOS = enablePOS

    def process_paragraph(self, paragraph, encoding='utf-8'):
        r = Result()

        n_sentence_total_number = 1
        n_term_total_number = 0
        n_term_numerals = len( find_numeral(paragraph) )
        n_term_in_dic = 0
        n_term_len_gte6 = 0

        n_term_len_gte4 = 0
        n_term_latin = 0

        n_term_at_mention = len( find_at_mention(paragraph) )
        n_term_emotion = len( find_emotions(paragraph) )
        n_term_hashtag = len( find_hashtag(paragraph) )
        n_term_url = len( find_url(paragraph) )

        lst = nlpir.Seg(paragraph)
        for t in lst:
            term = t[0].decode('utf-8','ignore')
            POS = t[1]

            n_term_total_number += 1

            if is_sentence_separator(term):    #如果是句子分隔符，句子数自增
                n_sentence_total_number += 1
            else:
                if is_latin(term): n_term_latin += 1
                if len(term)>=6:  n_term_len_gte6 += 1
                if len(term)>=4:  n_term_len_gte4 += 1

            tags = get_term_tags(term)
            if len(tags)>0:
                n_term_in_dic += 1
                for tag in tags:
                    r.accumulate(tag)

            if self.enablePOS: r.accumulate('POS/%s'%POS)

        r.accumulate('stat/WordCount', value=n_term_total_number)
        if n_term_total_number == 0: n_term_total_number=float('NaN')

        r.accumulate('stat/WordPerSentence', value= float(n_term_total_number)/n_sentence_total_number)
        r.accumulate('stat/RateDicCover', value= float(n_term_in_dic)/n_term_total_number)
        r.accumulate('stat/RateNumeral', value= float(n_term_numerals)/n_term_total_number)
        r.accumulate('stat/RateSixLtrWord', value= float(n_term_len_gte6)/n_term_total_number)

        r.accumulate('stat/RateFourCharWord', value= float(n_term_len_gte4)/n_term_total_number)
        r.accumulate('stat/RateLatinWord', value= float(n_term_latin)/n_term_total_number)

        r.accumulate('stat/NumAtMention', value=n_term_at_mention)
        r.accumulate('stat/NumEmotion', value=n_term_emotion)
        r.accumulate('stat/NumHashTag', value=n_term_hashtag)
        r.accumulate('stat/NumURLs', value=n_term_url)

        return r


    def process_file(self, file_path, file_encoding='utf-8-sig'):
        r = Result()

        n_sentence_total_number = 1
        n_term_total_number = 0
        n_term_numerals = 0
        n_term_in_dic = 0
        n_term_len_gte6 = 0

        n_term_len_gte4 = 0
        n_term_latin = 0

        n_term_at_mention = 0
        n_term_emotion = 0
        n_term_hashtag = 0
        n_term_url = 0

        with codecs.open(file_path, 'r', encoding=file_encoding) as fp:
            for line in fp:
                line = line.strip(' \t\r\n').encode('utf-8')
                if len(line)<1: continue

                n_term_numerals += len( find_numeral(line) )
                n_term_at_mention += len( find_at_mention(line) )
                n_term_emotion += len( find_emotions(line) )
                n_term_hashtag += len( find_hashtag(line) )
                n_term_emotion += len( find_url(line) )

                lst = nlpir.Seg(line)
                for t in lst:
                    term = t[0].decode('utf-8','ignore')
                    POS = t[1]

                    n_term_total_number += 1

                    if is_sentence_separator(term):    #如果是句子分隔符，句子数自增
                        n_sentence_total_number += 1
                    else:
                        if is_latin(term): n_term_latin += 1
                        if len(term)>=6:  n_term_len_gte6 += 1
                        if len(term)>=4:  n_term_len_gte4 += 1

                    tags = get_term_tags(term)
                    if len(tags)>0:
                        n_term_in_dic += 1
                        for tag in tags:
                            r.accumulate(tag)

                    if self.enablePOS: r.accumulate('POS/%s'%POS)

        r.accumulate('stat/WordCount', value=n_term_total_number)
        if n_term_total_number == 0: n_term_total_number=float('NaN')

        r.accumulate('stat/WordPerSentence', value=n_term_total_number/n_sentence_total_number)
        r.accumulate('stat/DicCoverRate', value=n_term_in_dic/n_term_total_number)
        r.accumulate('stat/Numerals', value=n_term_numerals/n_term_total_number)
        r.accumulate('stat/SixLtr', value=n_term_len_gte6/n_term_total_number)

        r.accumulate('stat/FourCharWord', value=n_term_len_gte4/n_term_total_number)
        r.accumulate('stat/Latin', value=n_term_latin/n_term_total_number)

        r.accumulate('stat/AtMention', value=n_term_at_mention)
        r.accumulate('stat/Emotion', value=n_term_emotion)
        r.accumulate('stat/HashTag', value=n_term_hashtag)
        r.accumulate('stat/URLs', value=n_term_url)

        return r

TextMind._dic = helper.terms
helper.load_all_dic()

if __name__ == '__main__':
    p = "Every dog has its own day. Big News: @解放日报 [最右]【呼市铁路局原副局长被判死缓 最头痛藏钱】2013年12月底，呼市铁路局原副局长马俊飞因受贿被判死缓。他说最头痛藏钱，从呼和浩特到北京，马俊飞又是购房又是租房，在挥之不去的恐惧中，人民币8800万、美元419万、欧元30万、港币27万，黄金43.3公斤，逐渐堆满了两所#房子#…… http://t.cn/8kgR6Yi"

    textMind = TextMind()

    r1 = textMind.process_paragraph(p)
    r2 = textMind.process_file(u'E:/ICTCLAS/ICTCLAS_2014_Beta/test/docs/0-两栖战车亮相.txt')
    r3 = textMind.process_file(u'E:/ICTCLAS/ICTCLAS_2014_Beta/test/docs/5.txt','GBK')

    print r1.dump(to_ration=False,contains_header=True,separator=',')
    print r2.dump(to_ration=False)
    print r3.dump()