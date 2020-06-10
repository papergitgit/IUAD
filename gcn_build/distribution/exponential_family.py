# python3
# -*- coding: utf-8 -*-
# @Author  : lina
# @Time    : 2018/5/3 14:45
"""
exponential family
"""
class ExponentialFamily():
    prob = 0   # double type,
    bernoulli_map = {}     # dict type, {Integer, Bernoulli}
    exponential_map = {}   # dict type, {Integer, Exponential}
    gaussian_map = {}      # dict type, {Integer, Gaussian}
    multinomial_map = {}   # dict type, {Integer, Multinomial}

    def set_prob(self, prob):
        self.prob = prob

    def get_prob(self):
        return self.prob

    def set_bernoulli_map(self, ber):
        self.bernoulli_map = ber

    def set_exponential_map(self, exp):
        self.exponential_map = exp

    def set_gaussian_map(self, gau):
        self.gaussian_map = gau

    def set_multinomial_map(self, mul):
        self.multinomial_map = mul

    def get_bernoulli_map(self):
        return self.bernoulli_map

    def get_exponential_map(self):
        return self.exponential_map

    def get_gaussian_map(self):
        return self.gaussian_map

    def get_multinomial_map(self):
        return self.multinomial_map

    def display(self):
        print("Output parameters of Bernoulli distribution： ")
        for key, value in self.bernoulli_map.items():
            print("bernoulli: ", key, "\t", value.get_prob1(), '\t', value.get_prob2())

        print("Output parameters of Exponential distribution： ")
        for key, value in self.exponential_map.items():
            print("Exponential: ", key, "\t", value.get_lambda1(), '\t', value.get_lambda2())

        print("Output parameters of Gaussian distribution： ")
        for key, value in self.gaussian_map.items():
            print("Gaussian: ", key, "\t", value.get_mu1(), '\t', value.get_mu2(), '\t', value.get_sigma1(), '\t', value.get_sigma2())

        print("Output parameters of Multinomial distribution： ")
        for key, value in self.multinomial_map.items():
            print("Multinomial: ", key, "\t", value.get_num_para(), '\t', value.get_prob1_all(), '\t', value.get_prob2_all())



