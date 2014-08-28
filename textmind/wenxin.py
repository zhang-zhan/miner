# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import codecs,re
import helper,result
import nlpir

class TextMind:
    def __init__(self, enablePOS = False):
        self.enablePOS = enablePOS

    def find_numeral(self, istr):
        r = re.findall(r"([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)",istr)
        return [t[0] for t in r]

    def find_url(self, istr):
        r = re.findall(r"((ht|f)tp(s?)\:\/\/[0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*(:(0-9)*)*(\/?)([a-zA-Z0-9\-‌​\.\?\,\'\/\\\+&amp;%\$#_]*)?)",istr)
        return [t[0] for t in r]

    def find_emotions(self,istr):
        r = re.findall(r"(\[(.{1,16}?)\])", istr)
        return [t[0] for t in r]

    def find_at_mention(self, istr):
        r = re.findall( r"(@[^\\s:：《]+([\\s:：《]|$)|#(.+?)#|http://t\\.cn/\\w+|\\[(.*?)\\])", istr )
        return [t[0] for t in r]

    def find_hashtag(self,istr):
        r = re.findall(r"(#(.{1,64}?)#)", istr)
        return [t[0] for t in r]

    def get_term_tags(self, term):
        tags = TextMind._dic.get(term,None)
        return tags if tags is not None else []

    def process_paragraph(self, paragraph, encoding=None):
        r = result.Result()

        n_sentence_total_number = 1
        n_term_total_number = 0
        n_term_numerals = len( self.find_numeral(paragraph) )
        n_term_in_dic = 0
        n_term_len_gte6 = 0

        n_term_len_gte4 = 0
        n_term_latin = 0

        n_term_at_mention = len( self.find_at_mention(paragraph) )
        n_term_emotion = len( self.find_emotions(paragraph) )
        n_term_hashtag = len( self.find_hashtag(paragraph) )
        n_term_url = len( self.find_url(paragraph) )

        lst = nlpir.Seg(paragraph)
        for t in lst:
            term = t[0].decode(encoding,'ignore') if encoding is not None else t[0]
            POS = t[1]

            if POS[0] == 'w':
                if POS in ['wj','ww','wt','wf']: #句号 问号 叹号 分号
                    n_sentence_total_number += 1
            else:
                n_term_total_number += 1
                if POS=='x':
                    n_term_latin += 1
                elif len(term)>=4:
                    n_term_len_gte4 += 1

            if len(term)>=6: n_term_len_gte6 += 1

            tags = self.get_term_tags(term)
            if len(tags)>0: n_term_in_dic += 1
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

        for k,v in r._results.iteritems():
            if k.startswith('textmind/'):
                r._results[k] = v / n_term_total_number * 100

        return r


    def process_file(self, file_path):
        r = result.Result()

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

        with codecs.open(file_path, 'r', encoding='utf-8-sig') as fp:
            for line in fp:
                line = line.strip(' \t\r\n').encode('utf-8')
                if len(line)<1: continue

                n_term_numerals += len( self.find_numeral(line) )
                n_term_at_mention += len( self.find_at_mention(line) )
                n_term_emotion += len( self.find_emotions(line) )
                n_term_hashtag += len( self.find_hashtag(line) )
                n_term_emotion += len( self.find_url(line) )

                lst = nlpir.Seg(line)
                for t in lst:
                    n_term_total_number += 1

                    term = t[0].decode('utf-8','ignore')
                    POS = t[1]

                    if POS[0] == 'w':
                        if POS in ['wj','ww','wt','wf']: #句号 问号 叹号 分号
                            n_sentence_total_number += 1
                        else:
                            n_term_total_number += 1
                            if POS=='x':
                                n_term_latin += 1
                            elif len(term)>=4:
                                n_term_len_gte4 += 1

                        if len(term)>=6: n_term_len_gte6 += 1

                        tags = self.get_term_tags(term)
                        if len(tags)>0: n_term_in_dic += 1
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

        for k,v in r._results.iteritems():
            if k.startswith('textmind/'):
                r._results[k] = v / n_term_total_number * 100

        return r

TextMind._dic = helper.terms
helper.load_all_dic()

if __name__ == '__main__':
    path = u'E:/ICTCLAS/ICTCLAS_2014_Beta/test/docs/0-两栖战车亮相.txt'
    p = "Every dog has its own day. Big News: @解放日报 [最右]【呼市铁路局原副局长被判死缓 最头痛藏钱】2013年12月底，呼市铁路局原副局长马俊飞因受贿被判死缓。他说最头痛藏钱，从呼和浩特到北京，马俊飞又是购房又是租房，在挥之不去的恐惧中，人民币8800万、美元419万、欧元30万、港币27万，黄金43.3公斤，逐渐堆满了两所#房子#…… http://t.cn/8kgR6Yi"

    textMind = TextMind()

    r = textMind.process_file(path)
    #r = textMind.process_paragraph(p)
    r2 = r.aggregate()
    print r
    print r2