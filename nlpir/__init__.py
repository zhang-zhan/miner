# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

#change this if you want use another NLP tool
tool = 'ltp' # should be one of (ltp, ictclas)

if tool == 'ltp':
    from ltp import Seg
elif tool == 'ictclas':
    from ictclas import Seg