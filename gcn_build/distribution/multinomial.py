# python3
# -*- coding: utf-8 -*-
# @Author  : lina
# @Time    : 2018/5/3 14:33
"""
distribution of multi
"""
class Multinomial():
    num_para = 0    # int type, parameters
    prob1 = []     # list type, parameter of matched pairs
    prob2 = []     # list type, parameter of unmatched pairs

    def __init__(self, num_para, prob1, prob2):
        self.num_para = num_para
        self.prob1 = prob1
        self.prob2 = prob2

    def set_para_and_prob(self, num_para, prob1, prob2):
        self.num_para = num_para
        self.prob1 = prob1
        self.prob2 = prob2

    def set_num_para(self, num_para):
        self.num_para = num_para

    def set_prob1(self, loc, value):
        self.prob1[loc] = value

    def set_prob2(self, loc, value):
        self.prob2[loc] = value

    def get_num_para(self):
        return self.num_para

    def get_prob1(self, loc):
        return self.prob1[loc]

    def get_prob2(self, loc):
        return self.prob2[loc]

    def get_prob1_all(self):
        return self.prob1

    def get_prob2_all(self):
        return self.prob2

    def to_string(self):
        print("numPara: ", self.num_para, "  prob1: ", self.prob1, "  prob2: ", self.prob2)
