# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

from collections import defaultdict
from maps import OrderedDefaultDict
from helper import terms, aggregate_tags

class Result:
    def __init__(self, tags=None):
        if len(terms)<1:
            raise ValueError('No dictionaries entries loaded yet!')

        self._results = OrderedDefaultDict(float)
        if tags is not None:
            Result.tags = tags
            for tag in tags: self._results[tag] = 0.0

    def __add__(self, other):
        for tag, val in other._results.iteritems():
            tval = self._results.get(tag,0.0)
            self._results[tag] = tval + other._results.get(tag)

    def __truediv__(self, v):
        for tag, val in self._results.iteritems():
            tval = self._results.get(tag,0)
            self._results[tag] = tval / v

    def __getitem__(self, item):
        return self._results.get(item, float('NaN'))

    def accumulate(self, tag, value=1):
        tval = self._results.get(tag,0.0)
        self._results[tag] = tval + value

    def stat(self):
        result = OrderedDefaultDict(float)
        ordered_tags = aggregate_tags()

        for tag in ordered_tags.values():
            result[tag] = 0.0

        added_tag = set()
        #traverse the result map
        for Tag,val in self._results.iteritems():
            tag = Tag.lower()

            try:
                ind = tag.rindex('/')
                tmp = tag[ind+1:]
            except ValueError as e:
                tmp = tag

            new_tag = ordered_tags.get(tmp,Tag)
            result[new_tag] = val
            added_tag.add(Tag)

        for k,v in self._results.iteritems():
            if k in added_tag:
                continue
            result[k] = v
        return result

    def aggregate(self):
        if len(self._results)<1:
            raise ValueError('Empty result, nothing to aggregate!')
        result = defaultdict(float)
        for tag,val in self._results.iteritems():
            try:
                ind = tag.rindex('/')
                suffix = tag[:ind]
            except ValueError:
                suffix = '%DEFAULT%'

            tval = result.get(suffix,0)
            result[suffix] = tval + val
        return result

    def __repr__(self):
        result = self.stat()
        r = '\t'.join( ['%.2f' % i for i in result.itervalues()] )
        return r

    def __str__(self):
        result = self.stat()
        r = '\t'.join( ['%s' % i for i in result.iterkeys()] )
        r += '\n' + '\t'.join( ['%.2f' % i for i in result.itervalues()] )
        return r

    def sum(self):
        return sum( [i for i in self._results.itervalues()] )
