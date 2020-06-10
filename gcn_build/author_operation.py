# python3
# -*- coding: utf-8 -*-
# @Author  : lina
# @Time    : 2018/7/29 10:05
import pymysql


def get_author_paper(connection):
    """
    get the (author, paper) pairs
    :param connection: mysql connection
    :return:
    """
    author_paper_list = []
    sql_select = "SELECT LOWER(name_handle), LOWER(paper_key) FROM author"
    cursor = connection.cursor()
    try:
        cursor.execute(sql_select)
        results = cursor.fetchall()
        for result in results:
            author_paper_list.append((result[0], result[1]))
    except Exception as e:
        print("Error: ", repr(e))
    return author_paper_list


def get_ignore_author(connection):
    """
    get the pairs whose name has less than two papers.
    :param connection:
    :return:
    """
    ignore_authors = set()
    sql_select = """
            SELECT LOWER(name_handle), LOWER(paper_key) FROM author WHERE LOWER(name_handle) IN
            (
            SELECT LOWER(temp.name_handle) FROM 
              (SELECT LOWER(name_handle) AS name_handle, count(*) AS count FROM author GROUP BY LOWER(name_handle)) temp
            WHERE temp.count <= 2 
            ) """
    cursor = connection.cursor()
    try:
        cursor.execute(sql_select)
        results = cursor.fetchall()
        for result in results:
            ignore_authors.add((result[0], result[1]))
    except Exception as e:
        print("Error: ", repr(e))
    return ignore_authors



