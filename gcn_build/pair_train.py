# python3
# -*- coding: utf-8 -*-
# @Author  : lina
# @Time    : 2018/8/22 14:38
import re
import math
import numpy as np
from nltk.corpus import stopwords
from gensim.models import word2vec
import networkx as nx
from WL_subtree_kernel import compute_mle_wl_kernel
from paper_dblp import PaperDblp


class PairTrain(object):

    paper_list1 = []    # init a PaperDblp type
    paper_list2 = []    # init a PaperDblp list type
    paper_coauthors = {}   # key is paper_key，value is a coauthor list
    co_papers_nums = {}   # key is name，value is the papers num of this name
    words_num = {}   # key is word，value is the frequency
    confs_num = {}
    model = None
    current_author = ""
    similarity = []   # list type


    def __init__(self,
                 paper_list1,
                 paper_list2,
                 paper_coauthors,
                 co_papers_nums,
                 words_num,
                 confs_num,
                 model,
                 current_author=""):
        """
        init the PairTrain.
        :param paper_list1:  dblp paper list of one vertex.
        :param paper_list2:  dblp paper list of another vertex.
        :param paper_coauthors: key is paper_key，value is a coauthor list
        :param co_papers_nums: key is name，value is the papers num of this name
        :param words_num: key is word，value is the frequency
        :param confs_num: key is conf, value is the frequency
        :param model: word2vec training result.
        :param current_author: current author
        """
        self.paper_list1 = paper_list1
        self.paper_list2 = paper_list2
        self.paper_coauthors = paper_coauthors
        self.co_papers_nums = co_papers_nums
        self.words_num = words_num
        self.confs_num = confs_num
        self.model = model
        self.current_author = current_author
        self.similarity = self.cal_similarity()


    def get_paper_list1(self):
        return self.paper_list1


    def get_paper_list2(self):
        return self.paper_list2


    def get_similarity(self):
        return self.similarity


    def to_string(self):
        print("paper list is::")
        for paper_temp in self.paper_list2:
            print(paper_temp.to_string())
        print("similarity is:: %s" % self.similarity)

    def cal_similarity(self):
        self.similarity = []
        self.similarity = self.cal_time_decay_word()
        self.similarity = self.cal_coauthor_triangle()
        self.similarity = self.wl_subtree_similarity()
        self.similarity = self.cal_conf_sim()
        self.similarity = self.cal_word2vec()
        self.similarity = self.cal_conf_exist()
        return self.similarity

    def get_conf_frequency(self, paper_list):
        """
        get the conf frequency of paper_list.
        :param paper_list:
        :return:
        """
        frequency = {}
        for paper in paper_list:
            frequency.setdefault(paper.get_conference().lower(), 0)
            frequency[paper.get_conference().lower()] += 1
        return frequency


    def cal_conf_exist(self):
        """
        similarity of representative community.
        :return:
        """
        min_paper_list = self.paper_list1 if len(self.paper_list1) < len(self.paper_list2) else self.paper_list2
        max_paper_list = self.paper_list1 if len(self.paper_list1) >= len(self.paper_list2) else self.paper_list2
        conf_number2 = self.get_conf_frequency(max_paper_list)  # key is conf, value is year list
        conf_number1 = self.get_conf_frequency(min_paper_list)  # key is conf, value is year list

        max_key_min = max(conf_number1, key=conf_number1.get)
        count_min = conf_number2.get(max_key_min, 0)
        max_key_max = max(conf_number2, key=conf_number2.get)
        count_max = conf_number1.get(max_key_max, 0)
        value = (count_min + count_max) / len(min_paper_list)

        self.similarity.append(value)
        return self.similarity


    def dot_product(self, v1, v2):
        return sum(a * b for a, b in zip(v1, v2))


    def magnitude(self, vector):
        return np.sqrt(self.dot_product(vector, vector))


    def get_average_word2vec(self, paper_list):
        frequent_word = stopwords.words('english')
        final_vector = np.array([0.0] * 100)
        count_1 = 0
        for key in paper_list:
            str_list = [elem for elem in re.split(r'[:： _+#-.\?"(),（）{}+=]', key.get_title().lower()) if
                         elem != '']
            for strs in str_list:
                if strs not in frequent_word and strs in self.model.wv.vocab.keys():
                    vector = self.model.wv[strs]
                    final_vector += np.array(vector)
                    count_1 += 1
        final_vector = final_vector / count_1

        return final_vector


    def cal_word2vec(self):
        """
        word2vec similarity.
        :return:
        """

        final_vector_1 = self.get_average_word2vec(self.paper_list1)
        final_vector_2 = self.get_average_word2vec(self.paper_list2)

        sim = self.dot_product(final_vector_1, final_vector_2) / (self.magnitude(final_vector_1) * self.magnitude(final_vector_2) + 0.0000000000001)
        sim = 0.5 + 0.5 * sim

        self.similarity.append(sim)
        return self.similarity


    def get_word_year_list(self, paper_list):
        # frequent_word = ["for", "of", "a", "and", "based", "in", "on", "the", "an"]
        words_year_dict = {}
        frequent_word = stopwords.words('english')
        for key in paper_list:
            str_list = [elem for elem in re.split(r'[:： _+#-.\?"(),（）{}+=]', key.get_title().lower()) if
                         elem != '']
            for strs in str_list:
                if strs not in frequent_word:
                    if words_year_dict.get(strs.strip()):
                        words_year_dict[strs.strip()].append(key.get_year())
                    else:
                        words_year_dict[strs.strip()] = [key.get_year()]
        return words_year_dict

    def cal_time_decay_word(self):
        """
        time consistence in research interest.
        """

        words_year_dict1 = self.get_word_year_list(self.paper_list1)
        words_year_dict2 = self.get_word_year_list(self.paper_list2)

        min_len_dict = words_year_dict1 if len(self.paper_list1) < len(self.paper_list2) else words_year_dict2
        max_len_dict = words_year_dict1 if len(self.paper_list1) >= len(self.paper_list2) else words_year_dict2

        sum = 0
        for word, years_list in min_len_dict.items():
            min_dist = 10000
            if max_len_dict.get(word):
                target_list = max_len_dict[word]
                for year in years_list:
                    dist = min(np.abs(np.array(target_list) - year))
                    if min_dist >= dist:
                        min_dist = dist
                # min(len(years_list), len(target_list)) is the co-exist frequency
                if self.words_num.get(word):
                    sum += np.exp(-0.62 * min_dist) * min(len(years_list), len(target_list)) / np.log(self.words_num.get(word) + 1)
        final_value = sum / min(len(self.paper_list1), len(self.paper_list2))

        self.similarity.append(final_value)
        return self.similarity

    def get_triangle_frequency(self, paper_list):
        """
        get the triangle frequency.
        :param paper_list:
        :return:
        """
        triangle_coauthors = {}
        for paper_key in paper_list:
            coauthors = [elem.lower() for elem in self.paper_coauthors.get(paper_key.get_paper_key())]
            length = len(coauthors)
            if length >= 3:
                for i in range(0, length - 2):
                    for j in range(i + 1, length - 1):
                        for k in range(j + 1, length):
                            if len({coauthors[i].lower(), coauthors[j].lower(), coauthors[k].lower()}) == 3:
                                min_v = min(coauthors[i].lower(),
                                            min(coauthors[j].lower(), coauthors[k].lower()))
                                max_v = max(coauthors[i].lower(),
                                            max(coauthors[j].lower(), coauthors[k].lower()))
                                mid_v = list(
                                    {coauthors[i].lower(), coauthors[j].lower(), coauthors[k].lower()} - {
                                        min_v, max_v})[0]
                                triangle_coauthors.setdefault((min_v, mid_v, max_v), 0)
                                triangle_coauthors[(min_v, mid_v, max_v)] += 1
        return triangle_coauthors

    def cal_coauthor_triangle(self):
        """
        calculate the triangle coincidence of two vertices.
        :return:
        """

        min_papers_list = self.paper_list1 if len(self.paper_list1) < len(self.paper_list2) else self.paper_list2
        max_papers_list = self.paper_list1 if len(self.paper_list1) >= len(self.paper_list2) else self.paper_list2
        min_triangle_coauthors = self.get_triangle_frequency(min_papers_list)
        max_triangle_coauthors = self.get_triangle_frequency(max_papers_list)

        total_sum = 0
        for key, value in min_triangle_coauthors.items():
            if max_triangle_coauthors.get(key):
                total_sum += min(value, max_triangle_coauthors[key])
        final_value = total_sum / min(len(self.paper_list1), len(self.paper_list2))

        self.similarity.append(final_value)
        return self.similarity


    def generate_graph(self, paper_list):
        """
        constrcut graph.
        :param paper_list:
        :return:
        """
        g = nx.Graph()  # graph of one vertex
        for paper in paper_list:
            coauthors = list(set(self.paper_coauthors[paper.get_paper_key()]))
            for i in range(0, len(coauthors) - 1):
                for j in range(i + 1, len(coauthors)):
                    g.add_edge(coauthors[i].lower(), coauthors[j].lower())
        return g


    def wl_subtree_similarity(self):
        """
        WL sub-graph kernel
        :return:
        """
        g1 = self.generate_graph(self.paper_list1)  # graph of one vertex
        g2 = self.generate_graph(self.paper_list2)  # graph of another vertex

        K = compute_mle_wl_kernel([g1, g2], h=1)
        sim = K[0][1] / np.sqrt(K[0][0] * K[1][1])

        self.similarity.append(sim)
        return self.similarity


    def cal_conf_sim(self):
        """
        similarity  of  research  community.
        :return:
        """
        min_list = self.paper_list1 if len(self.paper_list1) < len(self.paper_list2) else self.paper_list2
        max_list = self.paper_list1 if len(self.paper_list1) >= len(self.paper_list2) else self.paper_list2
        max_dict = self.get_conf_frequency(max_list)
        min_dict = self.get_conf_frequency(min_list)

        sum = 0
        for conf, value in min_dict.items():
            if max_dict.get(conf):
                co_value = min(value, max_dict[conf])
                sum += co_value / np.log(self.confs_num.get(conf) + 1)
        final_res = sum / min(len(self.paper_list1), len(self.paper_list2))
        self.similarity.append(final_res)
        return self.similarity











