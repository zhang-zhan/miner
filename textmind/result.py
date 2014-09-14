# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

from collections import defaultdict
from maps import OrderedDefaultDict
import helper

class Result:
    def __init__(self, tags=None):
        if len(helper.terms)<1:
            raise ValueError('No dictionaries entries loaded yet!')

        self._results = OrderedDefaultDict(float)
        if tags is not None:
            Result.tags = tags
            for tag in tags: self._results[tag] = 0

    def __add__(self, other):
        for tag, val in other._results.iteritems():
            tval = self._results.get(tag,0)
            self._results[tag] = tval + other._results.get(tag)

    def __truediv__(self, v):
        for tag, val in self._results.iteritems():
            tval = self._results.get(tag,0)
            self._results[tag] = tval / v

    def __getitem__(self, item):
        return self._results.get(item, float('NaN'))

    def sum(self):
        return sum( [i for i in self._results.itervalues()] )

    def accumulate(self, tag, value=1):
        tval = self._results.get(tag,0)
        self._results[tag] = tval + value

    def stat(self, to_ration=False, div_filter_prefix=['textmind/','punctuation/'], divisor_tag = 'stat/WordCount' ):
        result = OrderedDefaultDict(float)
        ordered_tags = helper.aggregate_tags()

        for tag in ordered_tags.values():
            result[tag] = 0

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

        if to_ration:
            if not isinstance(div_filter_prefix,list):
                div_filter_prefix = [div_filter_prefix]
            divisor = result.get(divisor_tag,0)
            if divisor==0:
                raise RuntimeError('Unable to find divisor tag [%s]!' % divisor_tag)
            for k,v in result.iteritems():
                for prefix in div_filter_prefix:
                    if k.startswith(prefix):
                        result[k] = 100.0 * v / divisor
                        break

        return result

    def aggregate(self):
        if len(self._results)<1:
            raise ValueError('Empty result, nothing to aggregate!')
        result_ = defaultdict(float)
        for tag,val in self._results.iteritems():
            try:
                ind = tag.rindex('/')
                suffix = tag[:ind]
            except ValueError:
                suffix = '%DEFAULT%'

            tval = result_.get(suffix,0)
            result_[suffix] = tval + val
        return result_

    def dump(self,to_ration=True, contains_header=False, separator='\t', fp=None):
        result = self.stat(to_ration=to_ration)
        r = separator.join( ['%s' % i for i in result.iterkeys()] ) + '\n' if contains_header else ''
        r += separator.join( ['%s' % i for i in result.itervalues()] )
        if fp is not None:
            fp.write(r)
        return r

    def __str__(self):
        return self.dump()

    def __repr__(self):
        return self.dump(contains_header=True)