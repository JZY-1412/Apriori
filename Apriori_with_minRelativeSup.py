import csv
import itertools
import numpy as np
import pandas as pd


class AprioriWithMinRelativeSup:

    def __init__(self, minsup, minconf, minlift, minRelativeSup, dataset):
        self.minsup = minsup
        self.minconf = minconf
        self.minlift = minlift
        self.minRelativeSup = minRelativeSup
        self.total_tran_num = len(dataset)
        self.dataset = dataset
        self.freq_itemsets = {}
        self.relative_freq_itemsets = {}
        self.assoc_rules = []
        self.item_index = {}
        self.index_item = {}

    def encode(self, items):
        for index in range(len(items)):
            self.item_index[items[index]] = index
            self.index_item[index] = items[index]
        for transaction in range(len(self.dataset)):
            for item in range(len(self.dataset[transaction])):
                self.dataset[transaction][item] = self.item_index[self.dataset[transaction][item]]

    def candi_itemsets_gen(self, freq_itemsets):
        candi_itemsets = set()
        freq_itemsets_num = len(freq_itemsets)
        if freq_itemsets_num > 1:
            max_length = len(freq_itemsets[0]) + 1
            all_index_combinations = itertools.combinations(range(freq_itemsets_num), 2)
            for index1, index2 in all_index_combinations:
                candi_itemset = freq_itemsets[index1] | freq_itemsets[index2]
                if len(candi_itemset) == max_length:
                    candi_itemsets.add(candi_itemset)
        return candi_itemsets

    def freq_itemsets_gen(self, candi_itemsets, pre_maxsubset):
        one_turn_freq_itemsets = []
        support_count_dict = {}
        current_maxsubset = 0
        check_relative = True
        if len(candi_itemsets) == 0:
            return one_turn_freq_itemsets, current_maxsubset
        if len(list(candi_itemsets)[0]) <= 2:
            check_relative = False
        for transaction in self.dataset:
            for itemset in candi_itemsets:
                if itemset.issubset(frozenset(transaction)):
                    support_count_dict[itemset] = support_count_dict.get(itemset, 0) + 1
        for itemset in support_count_dict:
            support = support_count_dict[itemset] / self.total_tran_num
            if support > current_maxsubset:
                current_maxsubset = support
            if check_relative:
                if support >= self.minsup:
                    self.freq_itemsets[itemset] = support
                    if support / pre_maxsubset >= self.minRelativeSup:
                        self.relative_freq_itemsets[itemset] = support
                    one_turn_freq_itemsets.append(itemset)
            else:
                if support >= self.minsup:
                    self.freq_itemsets[itemset] = support
                    self.relative_freq_itemsets[itemset] = support
                    one_turn_freq_itemsets.append(itemset)

        return one_turn_freq_itemsets, current_maxsubset

    def find_freq_itemsets(self):
        # get frequent itemset with length 1
        whole_data = np.concatenate(self.dataset)
        len1_candi_itemsets_counts = np.unique(whole_data, return_counts=True)
        unique_items = list(len1_candi_itemsets_counts[0])
        self.encode(unique_items)
        for index in range(len(unique_items)):
            unique_items[index] = self.item_index[unique_items[index]]
        len1_candi_itemsets_counts_dict = dict(zip(unique_items, len1_candi_itemsets_counts[1]))
        for itemset in len1_candi_itemsets_counts_dict:
            support = len1_candi_itemsets_counts_dict[itemset] / self.total_tran_num
            if support >= self.minsup:
                self.freq_itemsets[frozenset([itemset])] = support
        # get frequent itemset with length greater than 1
        one_turn_freq_itemsets = list(self.freq_itemsets.keys())
        maxsubset = None
        while len(one_turn_freq_itemsets) > 0:
            candi_itemsets = self.candi_itemsets_gen(one_turn_freq_itemsets)
            one_turn_freq_itemsets, maxsubset = self.freq_itemsets_gen(candi_itemsets, maxsubset)

    def find_assoc_rules(self):
        for itemset in self.relative_freq_itemsets:
            if len(itemset) > 1:
                for length in range(1, len(itemset)):
                    antecedents = itertools.combinations(itemset, length)
                    for antecedent in antecedents:
                        support = self.freq_itemsets[itemset]
                        antecedent = frozenset(antecedent)
                        consequent = itemset - antecedent
                        confidence = support / self.freq_itemsets[antecedent]
                        lift = confidence / self.freq_itemsets[consequent]
                        if confidence >= self.minconf and lift >= self.minlift:
                            self.assoc_rules.append([antecedent, consequent, lift, confidence, support])

    def get_freq_itemsets(self):
        self.find_freq_itemsets()
        decoded_freq_itemsets = []
        for codeset in self.relative_freq_itemsets:
            freq_itemset = []
            for code in codeset:
                freq_itemset.append(self.index_item[code])
            decoded_freq_itemsets.append([freq_itemset, self.relative_freq_itemsets[codeset]])
        return decoded_freq_itemsets

    def get_assoc_rules(self):
        self.find_assoc_rules()
        decoded_freq_assoc_rules = []
        for rule in self.assoc_rules:
            antecedent = []
            consequent = []
            for code in rule[0]:
                antecedent.append(self.index_item[code])
            for code in rule[1]:
                consequent.append(self.index_item[code])
            lift = rule[2]
            conf = rule[3]
            support = rule[4]
            decoded_freq_assoc_rules.append([antecedent, consequent, lift, conf, support])
        decoded_freq_assoc_rules = sorted(decoded_freq_assoc_rules, key=lambda x: (len(x[0] + x[1]), x[2], x[3], x[4]),
                                          reverse=True)
        return decoded_freq_assoc_rules


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


# data = read_csv_file("task1.csv", False)
data = read_csv_file("supermarket.csv", True)
# data = read_csv_file("supermarket.csv", False)
apriori = AprioriWithMinRelativeSup(0.1, 0.15, 0.2, 0.5, data)
itemsets = apriori.get_freq_itemsets()
rules = apriori.get_assoc_rules()
itemsets_dataframe = pd.DataFrame(np.array(itemsets, dtype=object), columns=["itemset", "support"])
rules_dataframe = pd.DataFrame(np.array(rules, dtype=object), columns=["antecedent", "consequent", "lift", "confidence", "support"])
print(len(itemsets))
print(len(rules))
