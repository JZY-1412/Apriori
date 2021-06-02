import csv
import itertools
import numpy as np
import pandas as pd
import time


# read data
def read_csv_file(file_name, remove_last):
    items = []
    with open(file_name) as file:
        reader = csv.reader(file, delimiter=",")
        for row in reader:
            if remove_last:
                row = row[:-1]
            items.append(row)
    return items


# write output
def write_result(file_name1, file_name2, freq_itemsets, rules):
    f1 = open(file_name1, "w")
    for itemsets in freq_itemsets:
        line = str(list(itemsets)) + "," + str(final_freq_set[itemsets]) + "\n"
        f1.write(line)
    f1.close()

    f2 = open(file_name2, "w")
    for rule in rules:
        itemset1 = str(rule["left"])
        itemset2 = str(rule["right"])
        support = str(rule["support"])
        conf = str(rule["conf"])
        lift = str(rule["lift"])
        line = itemset1 + "," + itemset2 + "," + support + "," + conf + "," + lift + "\n"
        f2.write(line)
    f2.close()


# candidate length 1 itemset
def buildC1(dataset):
    item1 = set(itertools.chain(*dataset))
    return [frozenset([i]) for i in item1]


# get frequent length 1 itemset
def ck_to_lk(dataset, ck, min_support):
    support = {}
    for row in dataset:
        for item in ck:
            if item.issubset(row):
                support[item] = support.get(item, 0) + 1
    total = len(dataset)
    return {k: v / total for k, v in support.items() if v / total >= min_support}


# get length-k+1 frequent itemset based on length-k frequent itemset
def lk_to_ck(lk_list):
    ck = set()
    lk_size = len(lk_list)
    if lk_size > 1:
        k = len(lk_list[0])
        for i, j in itertools.combinations(range(lk_size), 2):
            t = lk_list[i] | lk_list[j]
            if len(t) == k + 1:
                ck.add(t)
    return ck

# get all frequent itemset
def get_L_all(dataset, min_support):
    c1 = buildC1(dataset)
    L1 = ck_to_lk(dataset, c1, min_support)
    L_all = L1
    Lk = L1
    while len(Lk) > 1:
        lk_key_list = list(Lk.keys())
        ck = lk_to_ck(lk_key_list)
        Lk = ck_to_lk(dataset, ck, min_support)
        if len(Lk) > 0:
            L_all.update(Lk)
        else:
            break
    return L_all


# get association rules
def rules_from_item(item):
    left = []
    for i in range(1, len(item)):
        left.extend(itertools.combinations(item, i))
    return [(frozenset(le), frozenset(item.difference(le))) for le in left]


def rules_from_L_all(L_all, min_confidence, min_lift):
    rules = []
    for Lk in L_all:
        if len(Lk) > 1:
            rules.extend(rules_from_item(Lk))
    result = []
    for left, right in rules:
        support = L_all[left | right]
        confidence = support / L_all[left]
        lift = confidence / L_all[right]
        if confidence >= min_confidence and lift >= min_lift:
            result.append({"left": left, "right": right, "support": support, "conf": confidence, "lift": lift})
    return result


# encode
dataset = read_csv_file("task1.csv", False)
# dataset = read_csv_file("task1.csv", False)
items = set(itertools.chain(*dataset))
str_to_index = {}
index_to_str = {}
for index, item in enumerate(items):
    str_to_index[item] = index
    index_to_str[index] = item
for i in range(len(dataset)):
    for j in range(len(dataset[i])):
        dataset[i][j] = str_to_index[dataset[i][j]]
freq_set = get_L_all(dataset, 0.15)

rules = rules_from_L_all(freq_set, 0.8, 0)

final_freq_set = {}
for itemset in freq_set.keys():
    str_freq_set = []
    items = list(itemset)
    for item in items:
        str_item = index_to_str[item]
        str_freq_set.append(str_item)
    str_freq_set = frozenset(str_freq_set)
    final_freq_set[str_freq_set] = freq_set[itemset]
final_rules = []
for r in rules:
    str_left = []
    str_right = []
    left = list(r["left"])
    right = list(r["right"])
    for item in left:
        str_left.append(index_to_str[item])
    for item in right:
        str_right.append(index_to_str[item])
    support = r["support"]
    conf = r["conf"]
    lift = r["lift"]
    final_rules.append({"left": str_left, "right": str_left, "support": support, "conf": conf, "lift": lift})

# for i in final_freq_set:
#     print(list(i), final_freq_set[i])
# for r in final_rules:
#     print(r["left"], "->", r["right"], "support:", r["support"], "lift:", r["lift"])
print("number of frequent itemsets:", len(freq_set))
print("number of association rules:", len(rules))
write_result("frequent_itemset.txt", "rules.txt", final_freq_set, final_rules)
