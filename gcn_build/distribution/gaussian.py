# python3
# -*- coding: utf-8 -*-
# @Author  : lina
# @Time    : 2018/5/3 14:38
"""
distribution of gaussian
"""
class Gaussian():
    mu1 = 0     # double type, mean value of matched pairs
    mu2 = 0     # double type, mean value of unmatched pairs
    sigma1 = 0  # double type, variance of matched pairs, 方差
    sigma2 = 0  # double type, variance of unmatched pairs, 方差

    def __init__(self, mu1, mu2, sigma1, sigma2):
        self.mu1 = mu1
        self.mu2 = mu2
        self.sigma1 = sigma1
        self.sigma2 = sigma2

    def set_mu_and_sigma(self, mu1, mu2, sigma1, sigma2):
        self.mu1 = mu1
        self.mu2 = mu2
        self.sigma1 = sigma1
        self.sigma2 = sigma2

    def set_mu1(self, mu1):
        self.mu1 = mu1

    def set_mu2(self, mu2):
        self.mu2 = mu2

    def set_sigma1(self, sigma1):
        self.sigma1 = sigma1

    def set_sigma2(self, sigma2):
        self.sigma2 = sigma2

    def get_mu1(self):
        return self.mu1

    def get_mu2(self):
        return self.mu2

    def get_sigma1(self):
        return self.sigma1

    def get_sigma2(self):
        return self.sigma2

    def to_string(self):
        print("mu1: ", self.mu1, "  mu2: ", self.mu2, "  sigma1: ", self.sigma1, " sigma2: ", self.sigma2)