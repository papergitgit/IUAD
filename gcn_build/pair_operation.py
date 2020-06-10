# python3
# -*- coding: utf-8 -*-
# @Author  : lina
# @Time    : 2018/4/23 15:12

from pair_train import *
from paper_dblp import *
import random

def generate_clusters_train(matched_papers_dict,
                            author_new_map,
                            paper_dblps,
                            paper_coauthors,
                            co_papers_num,
                            words_num,
                            confs_num,
                            model):
    """
    generate vertex pairs.
    :param matched_papers_dict: extracted vertex whose size is larger than 1 from SCN.
    :param author_new_map: name and the mapping of real names.
    :param paper_dblps: papers info.
    :param paper_coauthors: paper and the corresponding coauthors.
    :param co_papers_num: get the paper number of one name
    :param words_num: get the frequency of one word
    :param confs_num: get the frequency of one conf
    :param model: word2vec
    :return:
    """

    pairs_train = set()  # every element is a PairTrain type
    records = 5000
    candidate_idx = set()
    authors_raws = list(author_new_map.keys())
    while len(candidate_idx) < records:
        idx = random.randint(0, len(authors_raws) - 1)
        candidate_idx.add(idx)

    # print("candidate_idx is::", candidate_idx)

    for idx in candidate_idx:
        author_raw = authors_raws[idx]
        authors_new = author_new_map.get(author_raw)   # based on the new name of this idx
        sample_number = min(5, len(authors_new))
        sample_new_names = random.sample(authors_new, sample_number)

        # constrcut matched pairs
        for name in sample_new_names:
            paper_list = matched_papers_dict[name]
            if len(paper_list) >= 40:
                temp = [i + 1 for i in np.arange(len(paper_list) - 2)]
                sample_slices = random.sample(temp, 9)
                for sample_slice in sample_slices:
                    list1 = paper_list[0:sample_slice]
                    list2 = paper_list[sample_slice:len(paper_list)]
                    list1_papers = [paper_dblps.get(key) for key in list1 if paper_dblps.get(key) != None]
                    list2_papers = [paper_dblps.get(key) for key in list2 if paper_dblps.get(key) != None]
                    matched_pair = PairTrain(list1_papers,
                                             list2_papers,
                                             paper_coauthors,
                                             co_papers_num,
                                             words_num,
                                             confs_num,
                                             model,
                                             author_raw.lower())
                    pairs_train.add(matched_pair)
            elif len(paper_list) >= 20:
                temp = [i + 1 for i in np.arange(len(paper_list) - 2)]
                sample_slices = random.sample(temp, 5)
                for sample_slice in sample_slices:
                    list1 = paper_list[0:sample_slice]
                    list2 = paper_list[sample_slice:len(paper_list)]
                    list1_papers = [paper_dblps.get(key) for key in list1 if paper_dblps.get(key) != None]
                    list2_papers = [paper_dblps.get(key) for key in list2 if paper_dblps.get(key) != None]
                    matched_pair = PairTrain(list1_papers,
                                             list2_papers,
                                             paper_coauthors,
                                             co_papers_num,
                                             words_num,
                                             confs_num,
                                             model,
                                             author_raw.lower())
                    pairs_train.add(matched_pair)
            elif len(paper_list) >= 10:
                temp = [i + 1 for i in np.arange(len(paper_list) - 2)]
                sample_slices = random.sample(temp, 2)
                for sample_slice in sample_slices:
                    list1 = paper_list[0:sample_slice]
                    list2 = paper_list[sample_slice:len(paper_list)]
                    list1_papers = [paper_dblps.get(key) for key in list1 if paper_dblps.get(key) != None]
                    list2_papers = [paper_dblps.get(key) for key in list2 if paper_dblps.get(key) != None]
                    matched_pair = PairTrain(list1_papers,
                                             list2_papers,
                                             paper_coauthors,
                                             co_papers_num,
                                             words_num,
                                             confs_num,
                                             model,
                                             author_raw.lower())
                    pairs_train.add(matched_pair)

        # construct unmatched pairs
        for i in range(0, len(sample_new_names) - 1):
            for j in range(i+1, len(sample_new_names)):
                paper_list_i = matched_papers_dict[sample_new_names[i]]
                paper_list_j = matched_papers_dict[sample_new_names[j]]
                if len(paper_list_i) >= 4 and len(paper_list_j) >= 4:
                    combines = [(len(paper_list_i), len(paper_list_j))]
                    for combine in combines:
                        list1 = paper_list_i[0:int(combine[0])]
                        list2 = paper_list_j[0:int(combine[1])]
                        list1_papers = [paper_dblps.get(key) for key in list1 if paper_dblps.get(key) != None]
                        list2_papers = [paper_dblps.get(key) for key in list2 if paper_dblps.get(key) != None]
                        unmatched_pair = PairTrain(list1_papers,
                                                   list2_papers,
                                                   paper_coauthors,
                                                   co_papers_num,
                                                   words_num,
                                                   confs_num,
                                                   model,
                                                   author_raw.lower())
                        pairs_train.add(unmatched_pair)
    return list(pairs_train)
