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
from gensim.models import word2vec
import pymysql
import jieba

"""
linkage function。
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

    paper_dblps, all_title = get_paper_dblp(connection)  # read dblp paper info in database.

    all_title_cut = jieba.cut(all_title)
    cut_result = ' '.join(all_title_cut)
    with open(settings.title_cut_path, 'w', encoding='utf8') as w:
        w.write(cut_result)
    w.close()

    author_paper_list_all = get_author_paper(connection)  # get all author-paper from author
    ignore_authors_set = get_ignore_author(connection)  # get ignored authors whose paper is less than 2.
    paper_coauthors = get_coauthors(connection)  # get all paper and the coauthors from concat_coauthors
    co_papers_num = get_copaper_num(connection)  # get the paper nums of one author
    words_num = get_words_num(connection)   # get the frequency of each word.
    confs_num = get_confs_num(connection)   # get the frequency of each conf.

    connection.close()

    sentences = word2vec.LineSentence(settings.title_cut_path)
    model = word2vec.Word2Vec(sentences, hs=1, workers=10, min_count=1, window=5, size=100)
    model.save(settings.wordvec_path)

    matched_papers_dict, matched_author_paper_set, author_new_map = get_matched_papers(settings.matched_file_name)

    print("len of matched_papers_dict::", len(matched_papers_dict))
    print("len of author_paper_list_all::", len(author_paper_list_all))
    print("len of ignore_authors_set::", len(ignore_authors_set))
    print("len of matched_author_paper_set::", len(matched_author_paper_set))
    print("len of paper_coauthors::", len(paper_coauthors))

    pairs_train = generate_clusters_train(matched_papers_dict,
                                          author_new_map,
                                          paper_dblps,
                                          paper_coauthors,
                                          co_papers_num,
                                          words_num,
                                          confs_num, model)

    print("pairs_train has contructed")
    print("len of pairs_train:: ", len(pairs_train))
    dist = ["exponential", "exponential", "exponential", "exponential", "exponential", "exponential"]  # 6 features
    fs = FellegiSunter(pairs_train)  # initialize a FellegiSunter class
    fs.set_distribution(dist)
    inferred = fs.paper_linkageEF(pairs_train)  # paper linkage
    print("learning parameters done！")

    # linkage
    for author_raw, author_new_names in author_new_map.items():
        i = 0
        while i < len(author_new_names):
            j = i + 1
            while j < len(author_new_names):
                list_1 = [paper_dblps.get(paper_temp) for paper_temp in matched_papers_dict.get(author_new_names[i]) if
                          paper_dblps.get(paper_temp) != None]
                list_2 = [paper_dblps.get(paper_temp) for paper_temp in matched_papers_dict.get(author_new_names[j]) if
                          paper_dblps.get(paper_temp) != None]
                pair_test = PairTrain(list_1,
                                      list_2,
                                      paper_coauthors,
                                      co_papers_num,
                                      words_num,
                                      confs_num,
                                      model,
                                      author_raw)
                merge_decision = fs.test_linkage_cluster(inferred, pair_test)
                if merge_decision >= 100:
                    matched_papers_dict[author_new_names[i]].extend(matched_papers_dict[author_new_names[j]])
                    del matched_papers_dict[author_new_names[j]]
                    del author_new_names[j]
                    i = 0
                    j = i + 1
                else:
                    j += 1
            i += 1

    with open(settings.gcn_path, 'w', encoding='utf8') as w:
        for key, value in matched_papers_dict.items():
            w.write(key + "\t" + ','.join(value) + "\n")
    w.close()

    end = datetime.datetime.now()
    print("total cost time：", end - start)

    # log_file.close()
    # sys.stdout = stdout_backup


if __name__ == '__main__':
    main()











