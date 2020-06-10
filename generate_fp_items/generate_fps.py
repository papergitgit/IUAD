# python3
# -*- coding: utf-8 -*-
# @Author  : lina
# @Time    : 2018/5/15 14:05
"""
generate fp itemset
"""
import fp_growth_py3_modify as fpg
import pymysql
import datetime


def read_data(connection):
    """
    read the input of fp-growth.
    :param connection: mysql connection
    :return:
    """
    authors_all = []  # [[],[],[]]，every list is the coauthor list of one paper.
    cursor = connection.cursor()
    sql_select = "SELECT LOWER(concat_handled_names) FROM concat_coauthors"
    cursor.execute(sql_select)
    results = cursor.fetchall()
    coauthors_list = []
    for row in results:
        coauthors = [elem for elem in row[0].split(',') if elem != '']
        for coauthor in coauthors:
            coauthors_list.append(coauthor)
        authors_all.append(coauthors_list)
        coauthors_list = []
    return authors_all


def save_to_mysql(connection, result):
    """
    save fp-items to mysql.
    :param connection:
    :param result:
    :return:
    """
    sql_insert = """
    INSERT INTO fp_items(name_handle1_lower, name_handle2_lower, fp_item) 
    VALUES("%s", "%s", %d)
    ON DUPLICATE KEY UPDATE name_handle1_lower=VALUES(name_handle1_lower)
    """
    cursor = connection.cursor()
    counter = 0
    for elem in result:
        itemset = elem[0]
        support = int(elem[1])
        cursor.execute(sql_insert % (itemset[0].replace('ü', 'v').replace("\"", "\'"), itemset[1].replace('ü', 'v').replace("\"", "\'"), support))
        counter += 1
        if counter % 5000 == 0:
            connection.commit()
            print("counter is:: %d" % counter)
    connection.commit()
    print("done with counter: %d " % counter)



def main():
    start = datetime.datetime.now()

    connection = pymysql.Connect(
        host="10.11.6.117",
        port=3306,
        user="itoffice",
        passwd="Dase115_",
        db="iuad",
        charset="utf8"
    )

    authors_all = read_data(connection)
    print("the length of authors_all::", len(authors_all))

    frequent_itemsets = fpg.find_frequent_itemsets(authors_all, minimum_support=2, include_support=True)

    result = []
    for itemset, support in frequent_itemsets:
        if len(itemset) == 2:
            result.append((itemset, support))

    save_to_mysql(connection, result)

    connection.close()

    end = datetime.datetime.now()
    print("total time is:: ", end - start)

if __name__ == '__main__':
    main()
