# python3
# -*- coding: utf-8 -*-
# @Author  : lina
# @Time    : 2018/5/17 21:40
"""
build network by frequent itemset based on triangle stability relationships.
"""
import networkx as nx
import read_data
import datetime
import sys
import pymysql

# set the maximization iterations
sys.setrecursionlimit(5000000)

G = nx.Graph()

item_flag = {}     # save the edges because of merging (constructing some name rule to denotes different nodes.)
add_flag = {}    # unhandled edges are added, flag=1 denotes the edge is added.
author_new_map = {}     # a dict，key is name，value is a list of real names.

# stable setting
MIN_STABLE_EDGES = 4
MIN_CONTACT_EDGES = 4


def build_graph(fp_items, name_threshold):
    """
    process of building network:
    1、add fp item to the graph, and do the following operations:
        (1)for each node of the edges:
            (i) get all nodes of name A, and their neighbors.
            (ii) judge whether triangle is contructed
            (iii) if triangle is contructed, merge the two nodes.
    [More details please analysis code, this logic is complex.]
    :param fp_items:
    :param name_threshold:
    :return: G, the contructed stable network.
    """
    global G
    count = 0
    for item, value in fp_items.items():
        count += 1

        stable_threshold0 = 4
        stable_threshold1 = 4
        if name_threshold.get(item[0]):
            stable_threshold0 = name_threshold.get(item[0])
        if name_threshold.get(item[1]):
            stable_threshold1 = name_threshold.get(item[1])
        MIN_STABLE_EDGES = min(stable_threshold0, stable_threshold1)
        if value >= MIN_STABLE_EDGES:    # value>=MIN_STABLE_EDGES，add as a stable relation.
            if not item_flag.get((item[0], item[1])) and not item_flag.get((item[1], item[0])):    # judge whether has added.
                # add edges
                node1_name = item[0] + "," + item[1] + str(value)  # construct the mapping rule to make nodes unique.
                node2_name = item[1] + "," + item[0] + str(value)
                G.add_edge(node1_name, node2_name)
                author_new_map.setdefault(item[0], [])
                author_new_map[item[0]].append(node1_name)
                author_new_map.setdefault(item[1], [])
                author_new_map[item[1]].append(node2_name)
                add_flag[(item[0], item[1])] = (node1_name, node2_name)  # set flag = 1
            else:
                if item_flag.get((item[0], item[1])):
                    node1_name = item_flag.get((item[0], item[1]))[0]
                    node2_name = item_flag.get((item[0], item[1]))[1]
                    item_flag.pop((item[0], item[1]))
                    add_flag[(item[0], item[1])] = (node1_name, node2_name)
                else:
                    node1_name = item_flag.get((item[1], item[0]))[0]
                    node2_name = item_flag.get((item[1], item[0]))[1]
                    item_flag.pop((item[1], item[0]))
                    add_flag[(item[1], item[0])] = (node1_name, node2_name)
                    item = (item[1], item[0])

            fix_node = [node2_name, node1_name]

            for i_out in range(0, 2):  # judge two nodes of the edge.
                # judge whether nodes need to merge
                names = author_new_map[item[i_out]]
                pairs = []
                neighbor_map = {}
                for name in names:
                    neighbors = G.neighbors(name)
                    for neighbor in neighbors:
                        pairs.append((neighbor, fix_node[i_out]))
                        neighbor_map[neighbor] = name

                i = 0     # to access pairs
                j = 0     # to update pairs
                while i < len(pairs):
                    if pairs[i][0] != pairs[i][1]:
                        concat_threshold0 = 4
                        concat_threshold1 = 4
                        if name_threshold.get(pairs[i][0].split(',')[0]):
                            concat_threshold0 = name_threshold.get(pairs[i][0].split(',')[0])
                        if name_threshold.get(pairs[i][1].split(',')[0]):
                            concat_threshold1 = name_threshold.get(pairs[i][1].split(',')[0])
                        MIN_CONTACT_EDGES = min(concat_threshold0, concat_threshold1)
                        result1 = fp_items.get((pairs[i][0].split(',')[0], pairs[i][1].split(',')[0]), MIN_CONTACT_EDGES-10)
                        result2 = fp_items.get((pairs[i][1].split(',')[0], pairs[i][0].split(',')[0]), MIN_CONTACT_EDGES-10)
                        if (result1 >= MIN_CONTACT_EDGES) or (result2 >= MIN_CONTACT_EDGES):  # if having relation
                            temp_node1 = neighbor_map.get(pairs[i][0], "-1")  # temp_node1,temp_node2 are the same real author.
                            temp_node2 = neighbor_map.get(pairs[i][1], "-1")
                            if temp_node1 != "-1" and temp_node2 != "-1" and temp_node1 != temp_node2:
                                G = nx.contracted_nodes(G, temp_node1, temp_node2)   # merge temp_node1 and temp_node2
                                add_flag_value1 = add_flag.get((pairs[i][0].split(',')[0], pairs[i][1].split(',')[0]), "nullnull")
                                add_flag_value2 = add_flag.get((pairs[i][1].split(',')[0], pairs[i][0].split(',')[0]), "nullnull")
                                item_flag_value1 = item_flag.get((pairs[i][0].split(',')[0], pairs[i][1].split(',')[0]), "nullnull")
                                item_flag_value2 = item_flag.get((pairs[i][1].split(',')[0], pairs[i][0].split(',')[0]), "nullnull")
                                if add_flag_value1 == "nullnull" and add_flag_value2 == "nullnull" and item_flag_value1 == "nullnull" and item_flag_value2 == "nullnull":
                                    G.add_edge(pairs[i][0], pairs[i][1])  # add
                                    item_flag[(pairs[i][0].split(',')[0], pairs[i][1].split(',')[0])] = (pairs[i][0], pairs[i][1])  # flag - 1
                                else:
                                    if add_flag_value1 != "nullnull":
                                        node1 = add_flag[(pairs[i][0].split(',')[0], pairs[i][1].split(',')[0])][0]
                                        node2 = add_flag[(pairs[i][0].split(',')[0], pairs[i][1].split(',')[0])][1]
                                    elif add_flag_value2 != "nullnull":
                                        node1 = add_flag[(pairs[i][1].split(',')[0], pairs[i][0].split(',')[0])][1]
                                        node2 = add_flag[(pairs[i][1].split(',')[0], pairs[i][0].split(',')[0])][0]
                                    elif item_flag_value1 != "nullnull":
                                        node1 = item_flag[(pairs[i][0].split(',')[0], pairs[i][1].split(',')[0])][0]
                                        node2 = item_flag[(pairs[i][0].split(',')[0], pairs[i][1].split(',')[0])][1]
                                    elif item_flag_value2 != "nullnull":
                                        node1 = item_flag[(pairs[i][1].split(',')[0], pairs[i][0].split(',')[0])][1]
                                        node2 = item_flag[(pairs[i][1].split(',')[0], pairs[i][0].split(',')[0])][0]
                                    else:
                                        print("No actions!")

                                    # update all info, to keep data consistency, this update is somewhat inefficient.
                                    if pairs[i][0] != node1:
                                        G = nx.contracted_nodes(G, node1, pairs[i][0])  # merge temp_node1 and temp_node2
                                        fix_node = [fix_node[0].replace(pairs[i][0], node1), fix_node[1].replace(pairs[i][0], node1)]  # change fix_node
                                        author_new_map[pairs[i][0].split(",")[0]].remove(pairs[i][0])
                                        # update add_flag
                                        for key1, value1 in add_flag.items():
                                            if value1[0] == pairs[i][0] or value1[1] == pairs[i][0]:
                                                add_flag[key1] = (value1[0].replace(pairs[i][0], node1), value1[1].replace(pairs[i][0], node1))
                                        # update item_flag，let temp_node2 = temp_node1
                                        for key2, value2 in item_flag.items():
                                            if value2[0] == pairs[i][0] or value2[1] == pairs[i][0]:
                                                item_flag[key2] = (value2[0].replace(pairs[i][0], node1), value2[1].replace(pairs[i][0], node1))
                                        for key, value in neighbor_map.items():
                                            if value == pairs[i][0]:
                                                neighbor_map[key] = node1
                                        # update pair info
                                        if i < len(pairs) - 1:
                                            j = i + 1
                                            while j < len(pairs):
                                                pairs[j] = (pairs[j][0].replace(pairs[i][0], node1), pairs[j][1].replace(pairs[i][0], node1))
                                                j += 1

                                    if pairs[i][1] != node2:
                                        G = nx.contracted_nodes(G, node2, pairs[i][1])  # merge temp_node1 and temp_node2
                                        fix_node = [fix_node[0].replace(pairs[i][1], node2), fix_node[1].replace(pairs[i][1], node2)]  # change fix_node
                                        author_new_map[pairs[i][1].split(",")[0]].remove(pairs[i][1])
                                        # update add_flag，let temp_node2 = temp_node1
                                        for key1, value1 in add_flag.items():
                                            if value1[0] == pairs[i][1] or value1[1] == pairs[i][1]:
                                                add_flag[key1] = (value1[0].replace(pairs[i][1], node2),
                                                                  value1[1].replace(pairs[i][1], node2))
                                        # update item_flag，let temp_node2=temp_node1
                                        for key2, value2 in item_flag.items():
                                            if value2[0] == pairs[i][1] or value2[1] == pairs[i][1]:
                                                item_flag[key2] = (value2[0].replace(pairs[i][1], node2), value2[1].replace(pairs[i][1], node2))
                                        for key, value in neighbor_map.items():
                                            if value == pairs[i][1]:
                                                neighbor_map[key] = node2
                                        # update pair
                                        if i < len(pairs) - 1:
                                            j = i + 1
                                            while j < len(pairs):
                                                pairs[j] = (pairs[j][0].replace(pairs[i][1], node2),
                                                            pairs[j][1].replace(pairs[i][1], node2))
                                                j += 1

                                fix_node = [fix_node[0].replace(temp_node2, temp_node1), fix_node[1].replace(temp_node2, temp_node1)]  # change fix_node
                                if temp_node2 != temp_node1:
                                    author_new_map[temp_node2.split(",")[0]].remove(temp_node2)
                                # update add_flag，let temp_node2=temp_node1
                                for key1, value1 in add_flag.items():
                                    if value1[0] == temp_node2 or value1[1] == temp_node2:
                                        add_flag[key1] = (value1[0].replace(temp_node2, temp_node1),
                                                          value1[1].replace(temp_node2, temp_node1))
                                # update item_flag，let temp_node2=temp_node1
                                for key2, value2 in item_flag.items():
                                    if value2[0] == temp_node2 or value2[1] == temp_node2:
                                        item_flag[key2] = (value2[0].replace(temp_node2, temp_node1), value2[1].replace(temp_node2, temp_node1))
                                for key, value in neighbor_map.items():
                                    if value == temp_node2:
                                        neighbor_map[key] = temp_node1
                                # update pair
                                if i < len(pairs) - 1:
                                    j = i + 1
                                    while j < len(pairs):
                                        pairs[j] = (pairs[j][0].replace(temp_node2, temp_node1), pairs[j][1].replace(temp_node2, temp_node1))
                                        j += 1
                            elif temp_node1 and temp_node2 and temp_node1 == temp_node2:
                                add_flag_value1 = add_flag.get((pairs[i][0].split(',')[0], pairs[i][1].split(',')[0]), "nullnull")
                                add_flag_value2 = add_flag.get((pairs[i][1].split(',')[0], pairs[i][0].split(',')[0]), "nullnull")
                                item_flag_value1 = item_flag.get((pairs[i][0].split(',')[0], pairs[i][1].split(',')[0]), "nullnull")
                                item_flag_value2 = item_flag.get((pairs[i][1].split(',')[0], pairs[i][0].split(',')[0]), "nullnull")
                                if add_flag_value1 == "nullnull" and add_flag_value2 == "nullnull" and item_flag_value1 == "nullnull" and item_flag_value2 == "nullnull":
                                    G.add_edge(pairs[i][0], pairs[i][1])  # add the edge of pair
                                    item_flag[(pairs[i][0].split(',')[0], pairs[i][1].split(',')[0])] = (
                                    pairs[i][0], pairs[i][1])  # flag = 1
                                else:
                                    if add_flag_value1 != "nullnull":
                                        node1 = add_flag[(pairs[i][0].split(',')[0], pairs[i][1].split(',')[0])][0]
                                        node2 = add_flag[(pairs[i][0].split(',')[0], pairs[i][1].split(',')[0])][1]
                                    elif add_flag_value2 != "nullnull":
                                        node1 = add_flag[(pairs[i][1].split(',')[0], pairs[i][0].split(',')[0])][1]
                                        node2 = add_flag[(pairs[i][1].split(',')[0], pairs[i][0].split(',')[0])][0]
                                    elif item_flag_value1 != "nullnull":
                                        node1 = item_flag[(pairs[i][0].split(',')[0], pairs[i][1].split(',')[0])][0]
                                        node2 = item_flag[(pairs[i][0].split(',')[0], pairs[i][1].split(',')[0])][1]
                                    elif item_flag_value2 != "nullnull":
                                        node1 = item_flag[(pairs[i][1].split(',')[0], pairs[i][0].split(',')[0])][1]
                                        node2 = item_flag[(pairs[i][1].split(',')[0], pairs[i][0].split(',')[0])][0]
                                    else:
                                        print("No Actions")

                                    # update data
                                    if pairs[i][0] != node1:
                                        G = nx.contracted_nodes(G, node1, pairs[i][0])  # merge temp_node1 and temp_node2
                                        fix_node = [fix_node[0].replace(pairs[i][0], node1),
                                                    fix_node[1].replace(pairs[i][0], node1)]
                                        author_new_map[pairs[i][0].split(",")[0]].remove(pairs[i][0])
                                        # update add_flag
                                        for key1, value1 in add_flag.items():
                                            if value1[0] == pairs[i][0] or value1[1] == pairs[i][0]:
                                                add_flag[key1] = (value1[0].replace(pairs[i][0], node1),
                                                                  value1[1].replace(pairs[i][0], node1))
                                        # update item_flag，let temp_node2=temp_node1
                                        for key2, value2 in item_flag.items():
                                            if value2[0] == pairs[i][0] or value2[1] == pairs[i][0]:
                                                item_flag[key2] = (value2[0].replace(pairs[i][0], node1),
                                                                   value2[1].replace(pairs[i][0], node1))
                                        for key, value in neighbor_map.items():
                                            if value == pairs[i][0]:
                                                neighbor_map[key] = node1
                                        # update pair
                                        if i < len(pairs) - 1:
                                            j = i + 1
                                            while j < len(pairs):
                                                pairs[j] = (pairs[j][0].replace(pairs[i][0], node1),
                                                            pairs[j][1].replace(pairs[i][0], node1))
                                                j += 1

                                    if pairs[i][1] != node2:
                                        G = nx.contracted_nodes(G, node2, pairs[i][1])  # merge temp_node1 and temp_node2
                                        fix_node = [fix_node[0].replace(pairs[i][1], node2),
                                                    fix_node[1].replace(pairs[i][1], node2)]
                                        author_new_map[pairs[i][1].split(",")[0]].remove(pairs[i][1])
                                        # update add_flag，let temp_node2=temp_node1
                                        for key1, value1 in add_flag.items():
                                            if value1[0] == pairs[i][1] or value1[1] == pairs[i][1]:
                                                add_flag[key1] = (value1[0].replace(pairs[i][1], node2),
                                                                  value1[1].replace(pairs[i][1], node2))
                                        # update item_flag，let temp_node2=temp_node1
                                        for key2, value2 in item_flag.items():
                                            if value2[0] == pairs[i][1] or value2[1] == pairs[i][1]:
                                                item_flag[key2] = (value2[0].replace(pairs[i][1], node2),
                                                                   value2[1].replace(pairs[i][1], node2))
                                        for key, value in neighbor_map.items():
                                            if value == pairs[i][1]:
                                                neighbor_map[key] = node2
                                        # update pair
                                        if i < len(pairs) - 1:
                                            j = i + 1
                                            while j < len(pairs):
                                                pairs[j] = (pairs[j][0].replace(pairs[i][1], node2),
                                                            pairs[j][1].replace(pairs[i][1], node2))
                                                j += 1
                    i += 1


def match_results(teachers, co_author_papers, scn_path):
    """
    extract results from built graph and save to the middle file.
    :param teachers: teacher info needed to extract.
    :param co_author_papers: cooperation info.
    :return:
    """
    global G
    paper_set_added = set()
    for teacher in teachers:
        teacher_papers = {}  # Key is author name，value is the papers
        if teacher in author_new_map.keys():
            teachers_in_graph = author_new_map[teacher]
        else:
            teachers_in_graph = []
        count = 1
        for teacher_in_graph in teachers_in_graph:   # read author
            papers_of_one_author = set()
            neighbors_list = [node.split(',')[0] for node in G.neighbors(teacher_in_graph)]
            neighbors_set = set(neighbors_list)   # collaborators
            for neighbor in neighbors_set:  # every pair(teacher, neighbor)
                if co_author_papers.get((teacher, neighbor)):
                    papers_of_one_author = papers_of_one_author | co_author_papers.get((teacher, neighbor))
                if co_author_papers.get((neighbor, teacher)):
                    papers_of_one_author = papers_of_one_author | co_author_papers.get((neighbor, teacher))
            paper_set_added = paper_set_added | papers_of_one_author
            teacher_papers[teacher + " " + str(count)] = papers_of_one_author
            count = count + 1
        with open(scn_path, 'a', encoding='UTF-8') as w:
            for key, value in teacher_papers.items():
                value = ','.join(value)
                msg = key + '\t' + value + '\n'
                w.write(msg)
        w.close()


def main():
    # stdout_backup = sys.stdout
    # # define the log file that receives your log info
    # log_file = open("message.log", "w", encoding='UTF-8')
    # # redirect print output to log file
    # sys.stdout = log_file

    connection = pymysql.Connect(
        host="10.11.6.117",
        port=3306,
        user="itoffice",
        passwd="Dase115_",
        db="iuad",
        charset="utf8"
    )

    start = datetime.datetime.now()
    author_paper_keys = read_data.read_copaper_keys(connection)  # read copaper data
    fp_items, co_author_papers = read_data.read_fp_items(connection, author_paper_keys)  # read fp items
    name_paper_count, name_threshold = read_data.read_teacher_nums(connection)
    build_graph(fp_items, name_threshold)  # build network
    teachers_list = read_data.read_teachers(connection)
    scn_path = "../data/scn_res.txt"
    match_results(teachers_list, co_author_papers, scn_path)
    connection.close()
    end = datetime.datetime.now()
    print("start time：%s，end time：%s，all cost time：%s" % (start, end, end - start))

    # log_file.close()
    # sys.stdout = stdout_backup


if __name__ == '__main__':
    main()




