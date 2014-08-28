# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

class Filter:
    def __init__(self,term_in_collection=None, tag_in_collection=None):
        self.term_in_collection  = term_in_collection
        self.tag_in_collection   = tag_in_collection

    def route(self,term, tag):
        gratify = 0L

        if '*' in term: gratify |= 1

        if self.term_in_collection is not None:
            if term in self.term_in_collection:
                gratify |= 2

        if self.tag_in_collection is not None:
            if tag in self.tag_in_collection:
                gratify |= 4

        return gratify