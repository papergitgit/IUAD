# python3
# -*- coding: utf-8 -*-
# @Author  : lina
# @Time    : 2018/4/23 9:39
"""
code function: some logic function about paper.
"""
from paper_dblp import *
import re
import pymysql


def get_paper_dblp(connection):
    '''
    read paper info from database and save this to a dict.
    :return: a dict, the key is PaperKey, the value is paperDblp.
    '''
    paper_dblps = {}
    sql_select = "SELECT LOWER(paper_key), LOWER(title), year FROM paper"
    cursor = connection.cursor()
    try:
        cursor.execute(sql_select)
        results = cursor.fetchall()
        for result in results:
            conf = re.findall(r".*/(.*?)/.*", result[0].lower())[0].strip()
            paper_dblps[result[0]] = PaperDblp(result[0], result[1].lower(), conf, result[2])
    except Exception as e:
        print("Error: ", repr(e))
    return paper_dblps

def get_matched_papers(matched_file_name):
    """
    read matched author-papers from text.
    :param matched_file_name: file name
    :return:
    """
    matched_papers_dict = {}
    author_new_map = {}
    matched_author_paper = set()
    with open(matched_file_name, 'r', encoding='utf-8') as f:
        results = f.readlines()
        for result in results:
            temp = result.strip().split('\t')
            if len(temp) == 2:
                author_raw_name = re.sub(r'[0-9]+', '', temp[0].lower()).strip()
                matched_papers_dict[temp[0].strip()] = [elem for elem in temp[1].lower().strip().split(",") if elem != '']
                author_new_map.setdefault(author_raw_name.lower(), [])
                author_new_map[author_raw_name.lower()].append(temp[0].lower().strip())
                for paper_key in [elem for elem in temp[1].lower().strip().split(",") if elem != '']:
                    matched_author_paper.add((author_raw_name.lower(), paper_key.lower()))
    f.close()
    return matched_papers_dict, matched_author_paper, author_new_map

def get_coauthors(connection):
    """
    get information of concat_coauthors
    :param connection:
    :return:
    """
    paper_coauthors = {}
    sql_select = "SELECT LOWER(paper_key), LOWER(concat_handled_names) FROM concat_coauthors"
    cursor = connection.cursor()
    try:
        cursor.execute(sql_select)
        results = cursor.fetchall()
        for result in results:
            coauthors = set([elem for elem in result[1].split(',') if elem != ''])
            paper_coauthors[result[0].strip()] = coauthors
    except Exception as e:
        print("Error: ", repr(e))
    return paper_coauthors


def get_copaper_num(connection):
    """
    get copaper number of a author.
    :param connection:
    :return:
    """
    co_papers_nums = {}
    sql_select = "SELECT LOWER(name_handle_lower), LOWER(concat_co_papers) FROM co_papers"
    cursor = connection.cursor()
    try:
        cursor.execute(sql_select)
        results = cursor.fetchall()
        for result in results:
            length = len([elem for elem in result[1].split(",") if elem != ''])
            co_papers_nums[result[0].strip()] = length
    except Exception as e:
        print("Error: ", repr(e))
    return co_papers_nums


def get_words_num(connection):
    """
    get the word frequency of title.
    :param connection:
    :return:
    """
    all_word_frequent = {}
    sql_select = "SELECT LOWER(title) FROM paper"
    cursor = connection.cursor()
    cursor.execute(sql_select)
    results = cursor.fetchall()
    for result in results:
        title = result[0]
        words_list = [elem for elem in re.split(r'[:： _+#-.\?"(),（）{}+=]', title) if elem != '']
        for word in words_list:
            all_word_frequent.setdefault(word, 0)
            all_word_frequent[word] += 1
    return all_word_frequent


def get_confs_num(connection):
    """
    get the frequency of conference.
    :param connection:
    :return:
    """
    all_conf_frequent = {}
    sql_select = """select LOWER(paper_key) from paper"""
    cursor = connection.cursor()
    cursor.execute(sql_select)
    results = cursor.fetchall()
    for result in results:
        conf_obj = re.match(r'.*/(.*)/.*', result[0])
        if conf_obj:
            conf = conf_obj.group(1).lower()
            all_conf_frequent.setdefault(conf, 0)
            all_conf_frequent[conf] += 1
    return all_conf_frequent
