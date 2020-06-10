# python3
# -*- coding: utf-8 -*-
# @Author  : lina
# @Time    : 2018/5/15 14:45

"""
read data to build graph
"""

def read_copaper_keys(connection):
    """
    read data of co_papers info
    :param connection: mysql connection
    :return:
    """
    author_paper_keys = {}  # dicts，save co_papers table info, key is the author name. value is a set of papers
    sql_select = "SELECT name_handle_lower, concat_co_papers FROM co_papers"
    cursor = connection.cursor()
    cursor.execute(sql_select)
    results = cursor.fetchall()
    for row in results:
        name_handle_lower = row[0].replace("\"", "\'")   # data handle
        paper_keys = row[1].split(',')
        papers = set()
        for paper_key in paper_keys:
            papers.add(paper_key)     # add to set
        author_paper_keys[name_handle_lower] = papers
    return author_paper_keys

def read_fp_items(connection, author_paper_keys):
    """
    get fp items and the cooperation papers.
    :param connection: mysql connection
    :param author_paper_keys: the papers of one name.
    :return:
    """
    fp_items = {}  # save fp items，key is (name1,name2)，value the fp value.
    co_author_papers = {}  # save coauthor info，key is a tuple(name1,name2)，value is a set {paper1,paper2,...}
    sql_select = "SELECT name_handle1_lower, name_handle2_lower, fp_item FROM fp_items"
    cursor = connection.cursor()
    cursor.execute(sql_select)
    results_items = cursor.fetchall()
    for item in results_items:
        name_handle1_lower = item[0].strip()
        name_handle2_lower = item[1].strip()
        value = item[2]
        fp_items[(name_handle1_lower, name_handle2_lower)] = value    # save fps
        name1_set_papers = author_paper_keys.get(name_handle1_lower)
        name2_set_papers = author_paper_keys.get(name_handle2_lower)
        if name1_set_papers and name2_set_papers:
            co_author_papers[(name_handle1_lower, name_handle2_lower)] = name1_set_papers & name2_set_papers    # get the cooperation papers.
    return fp_items, co_author_papers


def read_teachers(connection):
    """
    read teacher to extract results.
    :param connection:
    :return:
    """
    teachers_list = []
    sql_select = """SELECT DISTINCT(LOWER(XMPY)) FROM teacher"""
    cursor = connection.cursor()
    cursor.execute(sql_select)
    teachers = cursor.fetchall()
    for teacher in teachers:
        teachers_list.append(teacher[0])
    return teachers_list

def read_teacher_nums(connection):
    """
    read the set thresholds.
    :param connection:
    :return:
    """
    name_paper_count = {}
    name_threshold = {}
    sql_select = "SELECT LOWER(name_handle), COUNT(*) as count FROM coauthors GROUP BY name_handle"
    cursor = connection.cursor()
    cursor.execute(sql_select)
    results = cursor.fetchall()
    for result in results:
        name_paper_count[result[0].strip()] = result[1]
        if result[1] >= 1000:
            name_threshold[result[0].strip()] = 20
        elif result[1] >= 600:
            name_threshold[result[0].strip()] = 12
        elif result[1] >= 300:
            name_threshold[result[0].strip()] = 9
        elif result[1] >= 100:
            name_threshold[result[0].strip()] = 6
        elif result[1] >= 4:
            name_threshold[result[0].strip()] = 4
        else:
            name_threshold[result[0].strip()] = 4
    return name_paper_count, name_threshold


