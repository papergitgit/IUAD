# python3
# -*- coding: utf-8 -*-
# @Author  : lina
# @Time    : 2018/5/3 14:21
"""
distribution of bernoulli distribution
"""
class Bernoulli():
    prob1 = 0    # double type, parameter of matched pairs
    prob2 = 0    # double type, parameter of unmatched pairs

    def __init__(self, prob1, prob2):
        self.prob1 = prob1
        self.prob2 = prob2

    def set_prob(self, prob1, prob2):
        self.prob1 = prob1
        self.prob2 = prob2

    def set_prob1(self, prob1):
        self.prob1 = prob1

    def set_prob2(self, prob2):
        self.prob2 = prob2

    def get_prob1(self):
        return self.prob1

    def get_prob2(self):
        return self.prob2

    def to_string(self):
        print("prob1: ", self.prob1, "  prob2: ", self.get_prob2())
