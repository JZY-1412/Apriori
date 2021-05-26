import csv
import itertools
import numpy as np
import pandas as pd


def read_csv_file(file_name):
    items = []
    with open(file_name) as file:
        reader = csv.reader(file, delimiter=",")
        for row in reader:
            items.append(np.array(row))
    items = np.array(items, dtype=list)
    return items


def apriori(minsup, minconf, minlift, file_name):
    data = read_csv_file(file_name)

    # get all the combination of each transaction
    all_tran_itemsets = []
    for transaction in data:
        combs = []
        for comb_len in range(1, len(transaction) + 1):
            comb = list(itertools.combinations(transaction, comb_len))
            combs += comb
        all_tran_itemsets += combs
    all_tran_itemsets = np.array(all_tran_itemsets, dtype=tuple)


    # get the occurrence number of each combination appeared in tran_combs
    tran_combs, count = np.unique(all_tran_itemsets, return_counts=True)
    tran_combs_count_dict = dict(zip(tran_combs, count))

    # get needed parameters
    total_num_tran = len(data)
    whole_data = np.concatenate(data)
    unique_items_counts = np.unique(whole_data, return_counts=True)
    unique_items = unique_items_counts[0]
    itemset_max_len = len(unique_items)

    # loop through the combinations
    candidate_itemsets = []
    for itemset_len in range(1, itemset_max_len + 1):
        combs = list(itertools.combinations(unique_items, itemset_len))
        candidate_itemsets += combs
    candidate_itemsets = np.array(candidate_itemsets, dtype=tuple)

    # find supersets of each itemset
    superset_dict = {}
    for i in range(len(candidate_itemsets)):
        itemset_i = candidate_itemsets[i]
        for j in range(i, len(candidate_itemsets)):
            itemset_j = candidate_itemsets[j]
            if set(itemset_i).issubset(itemset_j):
                if itemset_i in superset_dict:
                    superset_dict[itemset_i].append(itemset_j)
                else:
                    superset_dict[itemset_i] = [itemset_j]

    # find frequent itemsets
    freq_itemsets = []
    infreq_itemsets = []
    for itemset in candidate_itemsets:
        if itemset in infreq_itemsets:
            continue
        if itemset in tran_combs_count_dict:
            count = tran_combs_count_dict[itemset]
        else:
            count = 0
        support = count / total_num_tran
        if support >= minsup:
            freq_itemsets.append(itemset)
        else:
            infreq_itemsets.append(itemset)
            infreq_itemsets += superset_dict[itemset]

    print(freq_itemsets)
    print(len(freq_itemsets))


# apriori(0.15, 0, 0, "supermarket_less.csv")
# apriori(0.15, 0, 0, "task1.csv")

"""
不记录所有的排列组合。
先找出 unique item，组成只有一个 item 的 itemset，然后检查 support，记录 infrequent itemset 和 frequent itemset。
生成排列组合，移除包含 infrequent itemset 的组合。检查 support，记录 。。。

不记录所有有的 transaction 的排列组合，要逐个检查计数来计算 support，防止内存溢出。
"""

def apriori_2(minsup, minconf, minlift, file_name):
    data = read_csv_file(file_name)

    # get unique items
    whole_data = np.concatenate(data)
    unique_items_counts = np.unique(whole_data, return_counts=True)
    unique_items = unique_items_counts[0]
    itemset_max_length = len(unique_items)
    
    # find frequent itemsets
    tran_num = len(data)
    freq_itemsets = []
    infreq_itemsets = []
    for itemset_length in range(1, itemset_max_length + 1):
        combs = list(itertools.combinations(unique_items, itemset_length))
        for comb in combs:
            for infreq_itemset in infreq_itemsets:
                if set(comb).issubset(set(infreq_itemset)):
                    continue
            support_count = 0
            for transaction in data:
                if set(comb).issubset(set(transaction)):
                    support_count += 1
            support = support_count / tran_num
            if support > minsup:
                freq_itemsets.append(comb)
            else:
                infreq_itemsets.append(comb)
    print(freq_itemsets)
    print(len(freq_itemsets))


    


apriori_2(0.15, 0, 0, "task1.csv")


"""
TEST SECTION
"""

# a = np.array([[1, 2]], dtype=object)
# b = np.array([[1, 2, 3]], dtype=object)
# c = np.concatenate((a, b), axis=0, dtype=object)
# print(c)
# d = np.append(a, b, axis=0)
# print(d)

# a = set([1, 2])
# b = set(np.array([2, 1, 3]))
# print(a.issubset(b))