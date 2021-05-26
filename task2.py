import csv
import itertools
import numpy as np
import pandas as pd


def read_csv_file(file_name, remove_last):
    items = []
    with open(file_name) as file:
        reader = csv.reader(file, delimiter=",")
        for row in reader:
            if remove_last:
                row = row[:-1]
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


def apriori_2(minsup, minconf, minlift, file_name, remove_last):
    data = read_csv_file(file_name, remove_last)

    # get unique items
    whole_data = np.concatenate(data)
    unique_items_counts = np.unique(whole_data, return_counts=True)
    unique_items = unique_items_counts[0]
    itemset_max_length = len(unique_items)
    
    # find frequent itemsets
    tran_num = len(data)
    freq_itemsets = []
    infreq_itemsets = []
    itemset_support_count_dict = {}
    for itemset_length in range(1, itemset_max_length + 1):
        combs = list(itertools.combinations(unique_items, itemset_length))
        for comb in combs:
            comb = frozenset(comb)
            frequent = True
            for infreq_itemset in infreq_itemsets:
                if set(comb).issubset(set(infreq_itemset)):
                    frequent = False
            if frequent:
                support_count = 0
                for transaction in data:
                    if comb.issubset(transaction):
                        support_count += 1
                support = support_count / tran_num
                itemset_support_count_dict[comb] = support
                if support > minsup:
                    freq_itemsets.append(comb)
                else:
                    infreq_itemsets.append(comb)

    # find rules
    # rules = []
    # all_subsets = np.array([])
    # for itemset in freq_itemsets:
    #     print("=" * 100)
    #     print(itemset)
    #     subsets = all_subsets.copy()
    #     for subset in subsets:
    #         print("    ", subset)
    #         if subset.issubset(itemset):
    #             conf = itemset_support_count_dict[itemset] / itemset_support_count_dict[itemset - subset]
    #             rule = (itemset - subset, subset, conf)
    #             if conf >= minconf and rule not in rules:
    #                 rules.append(rule)
    #                 print("        ", rule)
    #             else:
    #                 subsets = subsets[(subset.issubset(subsets))]
    #                 print("Pruned here:", subsets)
    #     all_subsets = np.append(all_subsets, itemset)
    
    # print(len(rules))



# apriori_2(0.5, 0, 0, "small_supermarket.csv", True)
apriori_2(0.15, 0.8, 0, "task1.csv", False)



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

# a = frozenset([1, 2]) - frozenset([1])
# b = {a: 1}
# print(a)

# a = np.array([frozenset([1])])
# b = frozenset([1])
# c = np.append(a, b)
# print(c)

# a = np.array([(2)])
# b = (1, 2)
# c = np.append(a, b)
# print(c)

a = np.array([frozenset([1])])
b = frozenset([1,2,3])
c = np.append(a, b)
print(c)