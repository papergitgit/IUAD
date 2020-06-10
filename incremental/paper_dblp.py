# python3
# -*- coding: utf-8 -*-
# @Author  : lina
# @Time    : 2018/4/22 21:50
"""
code function: definite a class of PaperDblp
Attributes:
    authorName, title, paper_key, conference, year, which all from dblp data
"""

class PaperDblp(object):

    paper_key = ""
    title = ""
    conference = ""
    year = 0

    def __init__(self, paper_key="", title="", conference="", year=0):
        '''
        init one paper of dblp.
        :param title: paper title 
        :param conference: the conference/ journal of one paper
        :param year: the published year of one paper.
        '''
        self.paper_key = paper_key
        self.title = title
        self.conference = conference
        self.year = year

    def to_string_title(self):
        print("title: %s" % (self.title))

    def get_paper_key(self):
        return self.paper_key

    def get_title(self):
        return self.title

    def get_conference(self):
        return self.conference

    def get_year(self):
        return self.year

    def to_string(self):
        '''
        print the info of one PaperDblp object.
        :return: 
        '''
        return "%s, %s, %s" % (self.title, self.conference, self.year)
