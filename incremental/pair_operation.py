# python3
# -*- coding: utf-8 -*-
# @Author  : lina
# @Time    : 2018/4/23 15:12
"""
code function: some function about paper pairs.
"""
from pair_train import *
from paper_dblp import *
import random


def generate_pairs_train_random(matched_papers_dict,
                                paper_dblps,
                                paper_coauthors,
                                co_papers_num,
                                words_num,
                                confs_num,
                                model):
    """
    generate vertex pairs.
    :param matched_papers_dict: extracted vertex whose size is larger than 1 from SCN.
    :param paper_dblps: papers info.
    :param paper_coauthors: paper and the corresponding coauthors.
    :param co_papers_num: get the paper number of one name
    :param words_num: get the frequency of one word
    :param confs_num: get the frequency of one conf
    :param model: word2vec
    :return:
    """

    pairs_train = set()  # every element is a PairTrain type
    records = 300
    candidate_idx = []

    author_news_list = []
    papers_group_list = []
    for author_new_name, papers_key in matched_papers_dict.items():
        author_news_list.append(author_new_name)
        papers_group_list.append(papers_key)

    print("len of papers_group_list::", len(papers_group_list))

    author_raws_sample = {}
    while len(candidate_idx) < records:
        idx = random.randint(0, len(papers_group_list) - 1)
        if idx not in candidate_idx:
            candidate_idx.append(idx)
            author_raw_cur = re.sub(r'[0-9]+', '', author_news_list[idx]).strip()
            author_raws_sample[idx] = author_raw_cur
    print("len of candiate_idx::", len(candidate_idx))
    print("len of author_raws_sample::", len(author_raws_sample))

    for index in candidate_idx:
        current_papers = papers_group_list[index]
        for cur_pap in current_papers:
            papers_list = [paper_dblps.get(paper_key_temp) for paper_key_temp in
                           (set(current_papers) - set([cur_pap])) if
                           paper_dblps.get(paper_key_temp) != None]
            if paper_dblps.get(cur_pap) and len(papers_list) > 0:
                pair = PairTrain([paper_dblps.get(cur_pap)],
                                 papers_list,
                                 paper_coauthors,
                                 co_papers_num,
                                 words_num,
                                 confs_num,
                                 model,
                                 author_raws_sample.get(index))
                pairs_train.add(pair)

            unmatched_index_set = set(candidate_idx) - {index}
            unmatched_index_set = random.sample(unmatched_index_set, 10)
            for unmatched_idx in unmatched_index_set:
                raw_name1 = author_raws_sample.get(index)
                raw_name2 = author_raws_sample.get(unmatched_idx)
                if raw_name1 == raw_name2:
                    cur_raw_name = raw_name1
                else:
                    cur_raw_name = ""
                if cur_pap not in papers_group_list[unmatched_idx]:
                    unmatched_papers_list = [paper_dblps.get(paper_key_temp) for paper_key_temp in papers_group_list[unmatched_idx] if paper_dblps.get(paper_key_temp) != None]
                    if paper_dblps.get(cur_pap) and len(unmatched_papers_list) > 0:
                        unmatch_rn = random.random()
                        unmatched_pair = PairTrain([paper_dblps.get(cur_pap)],
                                                   unmatched_papers_list,
                                                   paper_coauthors,
                                                   co_papers_num,
                                                   words_num,
                                                   confs_num,
                                                   model,
                                                   cur_raw_name)

                        sims = unmatched_pair.get_similarity()
                        if sims[0] == 0 and sims[1] == 0 and sims[2] == 0 and sims[3] == 0:
                            if unmatch_rn > 0 and unmatch_rn < 0.1:
                                pairs_train.add(unmatched_pair)
                        else:
                            if unmatch_rn > 0 and unmatch_rn < 0.2:
                                pairs_train.add(unmatched_pair)
    return list(pairs_train)

