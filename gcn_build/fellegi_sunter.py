# python3
# -*- coding: utf-8 -*-
# @Author  : lina
# @Time    : 2018/5/3 15:14
"""
functions of paperlinkage using exp family, mainly including:
    1. parameter infer, e_step and m_step to infer parameters which are in stable status
    2. generate the final decision, the weight is the probability of pair matching
"""

from distribution.bernoulli import *
from distribution.exponential_family import *
from distribution.exponential import *
from distribution.gaussian import *
from distribution.multinomial import *
from distribution import *
import math

class FellegiSunter():
    dist = []    # list type
    family = []   # dict type, {String, ArrayList<Integer>}
    pair_train_list = []  # list type, every element is a paper pair
    feature_num = 6    # the number of feature, also is the dimension number of similarity list.
    iteration = 50    # the times of iteration

    def __init__(self, pair_papers):
        self.pair_train_list = pair_papers

    def set_distribution(self, dist):
        '''
        :param input:  a string list of distributions
        :return: a initialized exp family
        '''
        self.dist = dist

    def paper_linkageEF(self, pairs_paper):
        '''
        :param pairs_paper: pairs_paper.
        :return: decision, a map type value, the key is weight, value is paper pairs.
        '''
        self.feature_number = len(pairs_paper[0].similarity)  # attribute number
        inferred = self.infer_parameter()  # Step1：initialization，e_step is to calculate expectation，m_step is to get maximunation
        print("final parameters are：")
        inferred.display()
        return inferred


    def test_linkage_cluster(self, inferred, pair_test):
        weight = 0
        sim = pair_test.get_similarity()   # double list
        for j in range(0, len(sim)):
            if j in inferred.get_bernoulli_map().keys():
                ber = inferred.get_bernoulli_map().get(j)
                if sim[j] >= 0:
                    weight = weight + sim[j] * math.log(ber.get_prob1()) + (1 - sim[j]) * math.log(1 - ber.get_prob1()) - sim[j] * math.log(ber.get_prob2()) - (1 - sim[j]) * math.log(1 - ber.get_prob2())
                    # weight = weight + sim[j] * math.log(ber.get_prob1()) - (1 - sim[j]) * math.log(1 - ber.get_prob2())
            if j in inferred.get_multinomial_map().keys():
                multi = inferred.get_multinomial_map().get(j)
                if sim[j] > 0.5:
                    weight = weight + math.log(multi.get_prob1(0)) - math.log(multi.get_prob2(0))
                elif sim[j] > -0.5:
                    weight = weight + math.log(multi.get_prob1(1)) - math.log(multi.get_prob2(1))
                elif sim[j] > -1.1:
                    weight = weight + math.log(multi.get_prob1(2)) - math.log(multi.get_prob2(2))
            if j in inferred.get_exponential_map().keys():
                exp = inferred.get_exponential_map().get(j)
                if sim[j] >= 0:
                    weight = weight + math.log(exp.get_lambda1() / exp.get_lambda2()) + (exp.get_lambda2() - exp.get_lambda1()) * sim[j]
            if j in inferred.get_gaussian_map().keys():
                gau = inferred.get_gaussian_map().get(j)
                if sim[j] >= 0:
                    weight = weight + math.log(gau.get_sigma2() / gau.get_sigma1()) / 2
                    weight = weight + (sim[j] - gau.get_mu2()) * (sim[j] - gau.get_mu2()) / (2 * gau.get_sigma2())
                    weight = weight - (sim[j] - gau.get_mu1())*(sim[j] - gau.get_mu1()) / (2 * gau.get_sigma1())
        return weight


    def infer_parameter(self):
        '''
        infer parameters until the parameters of distributions are been convergence.
        :return: 
        '''
        count = 0
        before = self.initialize(True)
        print("after initialization： ")
        before.display()
        while count < self.iteration:
            expectation = self.e_step(before)
            # print("e_step: ", expectation)
            before = self.m_step(expectation, before)
            # print("m_step: ", before)
            count = count + 1

        return before

    def e_step(self, before):
        '''
        :param before: ExponentialFamily before
        :return: 
        '''
        expectation = []    # double list
        for j in range(0, len(self.pair_train_list)):
            pair = self.pair_train_list[j]
            sim = pair.get_similarity()   # double list
            match = 1.0
            unmatch = 1.0
            for i in range(len(sim)):
                if sim[i] >= 0:
                    match = match * self.get_density(i, sim[i], "matched", before)
                    unmatch = unmatch * self.get_density(i, sim[i], "unmatched", before)
            if match == 0 and unmatch == 0:
                exp = 0
            else:
                exp = before.get_prob() * match / (before.get_prob() * match + (1 - before.get_prob()) * unmatch)
            expectation.append(exp)
        # print(expectation)
        return expectation


    def m_step(self, expectation, before):
        '''  
        :param expectation:  ArrayList<Double> expectation
        :param before: ExponentialFamily before
        :return: 
        '''
        para = self.initialize(True)   # ExponentialFamily
        prob = 0   # double type
        bernoulli_map = para.get_bernoulli_map()     # get bernoulli distrbutions map
        exponential_map = para.get_exponential_map()    # get exponential distrbutions map
        gaussian_map = para.get_gaussian_map()     # get gaussian distrbutions map
        multinomial_map = para.get_multinomial_map()     # get multinomial distrbutions map
        gua = None   # Gaussian
        ber = None    # Bernoulli
        exp = None   # Exponential
        multi = None   # Multinomial
        for i in range(0, len(self.pair_train_list)):
            pair = self.pair_train_list[i]
            sim = pair.get_similarity()   # double list
            for j in range(0, len(sim)):
                if self.dist[j] == "bernoulli":
                    ber = bernoulli_map.get(j)
                    # print("bernoulli_map is::%s, ber is::%s" % (bernoulli_map, ber))
                    if sim[j] >= 0:
                        ber.set_prob1(ber.get_prob1() + sim[j] * expectation[i])
                        ber.set_prob2(ber.get_prob2() + sim[j] * (1 - expectation[i]))
                    else:
                        ber.set_prob1(ber.get_prob1() + before.get_bernoulli_map().get(j).get_prob1() * expectation[i])
                        ber.set_prob2(ber.get_prob2() + before.get_bernoulli_map().get(j).get_prob2() * (1 - expectation[i]))
                    bernoulli_map[j] = ber
                elif self.dist[j] == "exponential":
                    exp = exponential_map.get(j)
                    if sim[j] >= 0:
                        exp.set_lambda1(exp.get_lambda1() + sim[j] * expectation[i])
                        exp.set_lambda2(exp.get_lambda2() + sim[j] * (1 - expectation[i]))
                    else:
                        exp.set_lambda1(exp.get_lambda1() + 1.0 / before.get_exponential_map().get(j).get_lambda1() * expectation[i])
                        exp.set_lambda2(exp.get_lambda2() + 1.0 / before.get_exponential_map().get(j).get_lambda2() * (1 - expectation[i]))
                    exponential_map[j] = exp
                elif self.dist[j] == "gaussian":
                    gau = gaussian_map.get(j)
                    if sim[j] >= 0:
                        gau.set_mu1(gau.get_mu1() + sim[j] * expectation[i])
                        gau.set_mu2(gau.get_mu2() + sim[j] * (1 - expectation[i]))
                    else:
                        gau.set_mu1(gau.get_mu1() + before.get_gaussian_map().get(j).get_mu1() * expectation[i])
                        gau.set_mu2(gau.get_mu2() + before.get_gaussian_map().get(j).get_mu2() * (1 - expectation[i]))
                    gaussian_map[j] = gau
                elif self.dist[j] == "multinomial":
                    multi = multinomial_map.get(j)
                    if sim[j] >= 0.5:
                        multi.set_prob1(0, multi.get_prob1(0) + expectation[i])
                        multi.set_prob2(0, multi.get_prob2(0) + (1.0 - expectation[i]))
                    elif sim[j] > (-0.5):
                        multi.set_prob1(1, multi.get_prob1(1) + expectation[i])
                        multi.set_prob2(1, multi.get_prob2(1) + (1.0 - expectation[i]))
                    elif sim[j] > (-1.1):
                        multi.set_prob1(2, multi.get_prob1(2) + expectation[i])
                        multi.set_prob2(2, multi.get_prob2(2) + (1.0 - expectation[i]))
                    else:
                        print("The similarity value in multinomial distribution is not existing!")
                else:
                    print("There is not the distribution!")
            prob = prob + expectation[i]
        # end for
        # parameter update
        for key, value in bernoulli_map.items():
            value.set_prob1(value.get_prob1() / prob)
            value.set_prob2(value.get_prob2() / (len(expectation) - prob))
        for key, value in exponential_map.items():
            value.set_lambda1(prob / value.get_lambda1())
            value.set_lambda2((len(expectation) - prob) / value.get_lambda2())
        for key, value in multinomial_map.items():
            num = value.get_num_para()
            for i in range(0, num):
                value.set_prob1(i, value.get_prob1(i) / prob)
                value.set_prob2(i, value.get_prob2(i) / (len(expectation) - prob))
        for key, value in gaussian_map.items():
            value.set_mu1(value.get_mu1() / prob)
            value.set_mu2(value.get_mu2() / (len(expectation) - prob))
        for i in range(0, len(self.pair_train_list)):
            pair = self.pair_train_list[i]
            sim = pair.get_similarity()   # double list
            for j in range(0, len(sim)):
                if j in gaussian_map.keys():
                    gau = gaussian_map.get(j)
                    if sim[j] >= 0:
                        gau.set_sigma1(gau.get_sigma1() + (sim[j] - gau.get_mu1())*(sim[j] - gau.get_mu1()) * expectation[i])
                        gau.set_sigma2(gau.get_sigma2() + (sim[j] - gau.get_mu2())*(sim[j] - gau.get_mu2())*(1 - expectation[i]))
                    else:
                        gau.set_sigma1(gau.get_sigma1() + (before.get_gaussian_map().get(j).get_mu1() - gau.get_mu1())*(before.get_gaussian_map().get(j).get_mu1() - gau.get_mu1()) * expectation[i])
                        gau.set_sigma2(gau.get_sigma2() + (before.get_gaussian_map().get(j).get_mu2() - gau.get_mu2())*(before.get_gaussian_map().get(j).get_mu2() - gau.get_mu2())*(1 - expectation[i]))
        for key, value in gaussian_map.items():
            value.set_sigma1(value.get_sigma1() / prob)
            value.set_sigma2(value.get_sigma2() / (len(expectation) - prob))

        prob = prob / len(expectation)
        # print("m_step::: prob is:::", prob)

        para.set_prob(prob)
        para.set_bernoulli_map(bernoulli_map)
        para.set_exponential_map(exponential_map)
        para.set_gaussian_map(gaussian_map)
        para.set_multinomial_map(multinomial_map)

        print("m_step: ")
        para.display()
        return para


    def get_density(self, location, sim, group, before):
        '''
        int location, double sim, String group, ExponentialFamily before
        :param location: 
        :param sim: 
        :param group: 
        :param before: 
        :return: 
        '''
        probability = 0    # double type
        if self.dist[location] == "gaussian":
            gau = before.get_gaussian_map().get(location)   #Gaussian
            if(group == "matched"):
                probability = 1.0 / math.sqrt(2.0 * math.pi * gau.get_sigma1()) * math.exp(- 1.0 * (sim - gau.get_mu1()) * (sim - gau.get_mu1()) / (2 * gau.get_sigma1()))
            else:
                probability = 1.0 / math.sqrt(2.0 * math.pi * gau.get_sigma2()) * math.exp(- 1.0 * (sim - gau.get_mu2()) * (sim - gau.get_mu2()) / (2 * gau.get_sigma2()))
        elif self.dist[location] == "bernoulli":
            ber = before.get_bernoulli_map().get(location)   #Bernoulli
            if group == "matched":
                probability = math.pow(ber.get_prob1(), sim) * math.pow((1 - ber.get_prob1()), (1 - sim))
            else:
                probability = math.pow(ber.get_prob2(), sim) * math.pow((1 - ber.get_prob2()), (1 - sim))
        elif self.dist[location] == "exponential":
            exp = before.get_exponential_map().get(location)   # Exponential
            if group == "matched":
                probability = exp.get_lambda1() * math.pow(math.e, (-1.0 * sim * exp.get_lambda1()));
                # print("matched, get denstity probabilitu::", probability)
            else:
                probability = exp.get_lambda2() * math.pow(math.e, (-1.0 * sim * exp.get_lambda2()));
                # print("unmatched, get denstity probabilitu::", probability)
        elif self.dist[location] == "multinomial":
            multi = before.get_multinomial_map().get(location)   # Multinomial
            if group == "matched":
                if sim > 0.5:
                    probability = multi.get_prob1(0)
                elif sim > -0.5:
                    probability = multi.get_prob1(1)
                elif sim > -1.1:
                    probability = multi.get_prob1(2)
                else:
                    print("The similarity value for multinomial distrubtion is not existing!")
            else:
                if sim > 0.5:
                    probability = multi.get_prob2(0)
                elif sim > -0.5:
                    probability = multi.get_prob2(1)
                elif sim > -1.1:
                    probability = multi.get_prob2(2)
                else:
                    print("The similarity value for multinomial distrubtion is not existing!")
        else:
            print("The type of distribution is not existing!!")

        return probability


    def initialize(self, beginning):
        '''
        initialize the exp family.
        :param beginning: boolean value
        :return: return a exponentialFamily
        '''
        ef = ExponentialFamily()
        bernoulli_map = {}   # dict, {Integer, Bernoulli}
        bernoulli_map = {}   # dict
        exponential_map = {}  # dict
        gaussian_map = {}    # dict
        multinomial_map = {}  # dict
        if beginning:
            for i in range(0, len(self.dist)):
                if self.dist[i] == "bernoulli":
                    ber = Bernoulli(0.9, 0.1)
                    bernoulli_map[i] = ber
                elif self.dist[i] == "exponential":
                    exp = None
                    if i == 1:
                        exp = Exponential(2.0, 3.0)
                    elif i == 3:
                        exp = Exponential(2.0, 3.0)
                    else:
                        exp = Exponential(2.0, 3.0)
                    exponential_map[i] = exp
                elif self.dist[i] == "gaussian":
                    guu = None
                    gau = Gaussian(1.0, 0.0, 1.0, 1.0)
                    gaussian_map[i] = gau
                elif self.dist[i] == "multinomial":
                    prob1 = []   # list type
                    prob2 = []   # list type
                    dimen = 3
                    for k in range(0, dimen):
                        prob1.append(0.33)
                        prob1.append(0.33)
                        prob1.append(1-0.66)

                        prob2.append(0.33)
                        prob2.append(0.33)
                        prob2.append(1-0.66)
                    mul = Multinomial(dimen, prob1, prob2)
                    multinomial_map[i] = mul
                else:
                    print("Error!!! There is not the distribution!")
            ef.set_prob(0.5)
        else:
            for i in range(0, len(self.dist)):
                if self.dist[i] == "bernoulli":
                    ber = Bernoulli(0.0, 0.0)
                    bernoulli_map[i] = ber
                elif self.dist[i] == "exponential":
                    exp = Exponential(0.0, 0.0)
                    exponential_map[i] = exp
                elif self.dist[i] == "gaussian":
                    gau = Gaussian(0.0, 0.0, 0.0, 0.0)
                    gaussian_map[i] = gau
                elif self.dist[i] == "multinomial":
                    prob = []   # double list type
                    dimen = 3
                    for k in range(0, dimen):
                        prob.append(0.0)
                        prob.append(0.0)
                        prob.append(0.0)
                    multi = Multinomial(dimen, prob, prob)
                    multinomial_map[i] = multi
                else:
                    print("Error!!! There is not the distribution!")
            ef.set_prob(0.0)
        ef.set_bernoulli_map(bernoulli_map)
        ef.set_exponential_map(exponential_map)
        ef.set_gaussian_map(gaussian_map)
        ef.set_multinomial_map(multinomial_map)
        return ef

