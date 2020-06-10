# python3
# -*- coding: utf-8 -*-
# @Author  : lina
# @Time    : 2018/4/22 22:32
from paper_operation import *
from pair_operation import *
from fellegi_sunter import FellegiSunter
from author_operation import *
import datetime
import settings
from copy import deepcopy
import time
import sys
import pymysql
from gensim.models import word2vec


"""
linkage function.
"""

def main():
    # stdout_backup = sys.stdout
    # # define the log file that receives your log info
    # log_file = open("message.log", "w", encoding='UTF-8')
    # # redirect print output to log file
    # sys.stdout = log_file

    start = datetime.datetime.now()

    connection = pymysql.Connect(
        host="10.11.6.117",
        port=3306,
        user="itoffice",
        passwd="Dase115_",
        db="iuad",
        charset="utf8"
    )

    model = word2vec.Word2Vec.load(settings.wordvec_path)

    paper_dblps = get_paper_dblp(connection)  # read dblp paper info in database.
    author_paper_list_all = get_author_paper(connection)  # get all author-paper from author
    ignore_authors_set = get_ignore_author(connection)  # get ignored authors whose paper is less than 2.
    paper_coauthors = get_coauthors(connection)  # get all paper and the coauthors from concat_coauthors
    co_papers_num = get_copaper_num(connection)  # get the paper nums of one author
    words_num = get_words_num(connection)  # get the frequency of each word.
    confs_num = get_confs_num(connection)  # get the frequency of each conf.
    matched_papers_dict, matched_author_paper_set, author_new_map = get_matched_papers(settings.matched_file_name)

    matched_papers_dict_copy = deepcopy(matched_papers_dict)
    need_add_author_paper_set = set(author_paper_list_all) - ignore_authors_set - matched_author_paper_set

    print("len of matched_papers_dict::", str(len(matched_papers_dict)))
    print("len of author_paper_list_all::", len(author_paper_list_all))
    print("len of ignore_authors_set::", len(ignore_authors_set))
    print("len of matched_author_paper_set::", len(matched_author_paper_set))
    print("len of need_add_author_paper_set:::", len(need_add_author_paper_set))
    print("len of paper_coauthors::", len(paper_coauthors))

    pairs_train = generate_pairs_train_random(matched_papers_dict,
                                              paper_dblps,
                                              paper_coauthors,
                                              co_papers_num,
                                              words_num,
                                              confs_num,
                                              model)

    print("pairs_train has contructed")
    print("len of pairs_train:: ", len(pairs_train))
    dist = ["exponential", "exponential", "exponential", "exponential", "exponential", "exponential"]  # 6 features
    fs = FellegiSunter(pairs_train)  # initialize a FellegiSunter class
    fs.set_distribution(dist)
    inferred = fs.paper_linkageEF(pairs_train)  # paper linkage
    print("learning parameters done！")

    # linkage
    count = 0
    for elem in need_add_author_paper_set:
        pairTest = []
        author_raw_name = elem[0]
        need_paper_key = elem[1]
        if author_new_map.get(author_raw_name):
            for author_new in author_new_map.get(author_raw_name):
                construct_list = [paper_dblps.get(paper_temp) for paper_temp in matched_papers_dict.get(author_new) if
                                  paper_dblps.get(paper_temp) != None]
                if paper_dblps.get(need_paper_key) and len(construct_list) > 0:
                    pair_test = PairTrain([paper_dblps.get(need_paper_key)],
                                          construct_list,
                                          paper_coauthors,
                                          co_papers_num,
                                          words_num,
                                          confs_num,
                                          model,
                                          author_raw_name)
                    pairTest.append((pair_test, author_new))
            author_added_name, max_weight = fs.test_linkage_single(inferred, pairTest)
            if max_weight >= 100:
                matched_papers_dict_copy[author_added_name].append(need_paper_key)

    with open(settings.incremental_path, 'w', encoding='utf-8') as w:
        for author_new_name, paper_list_result in matched_papers_dict_copy.items():
            papers = ','.join(paper_list_result)
            w.write(author_new_name + '\t' + papers + '\n')
    w.close()

    end = datetime.datetime.now()
    print("total cost time: ", end - start)

    # log_file.close()
    # sys.stdout = stdout_backup

if __name__ == '__main__':
    main()











