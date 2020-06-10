# python3
# -*- coding: utf-8 -*-
# @Author  : lina
# @Time    : 2018/5/3 14:27
"""
distribution of exponential.
"""
class Exponential():
    lambda1 = 0     # double type, parameter of matched pairs
    lambda2 = 0     # double type, parameter of unmatched pairs

    def __init__(self, lambda1, lambda2):
        self.lambda1 = lambda1
        self.lambda2 = lambda2

    def set_lambda(self, lambda1, lambda2):
        self.lambda1 = lambda1
        self.lambda2 = lambda2

    def set_lambda1(self, lambda1):
        self.lambda1 = lambda1

    def set_lambda2(self, lambda2):
        self.lambda2 = lambda2

    def get_lambda1(self):
        return self.lambda1

    def get_lambda2(self):
        return self.lambda2

    def to_string(self):
        print("lambda1: ", self.lambda1, "  lambda2: ", self.lambda2)
