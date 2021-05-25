import csv
import itertools
import numpy as np

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
    tran_combs_count_dict =  dict(zip(tran_combs, count))

    # get needed parameters
    total_num_tran = len(data)
    whole_data = np.concatenate(data)
    unique_items_counts = np.unique(whole_data, return_counts=True)
    unique_items = unique_items_counts[0]
    itemset_max_len = len(unique_items)

    # loop through the combinations
    condidate_itemsets = []
    for itemset_len in range(1, itemset_max_len + 1):
        combs = list(itertools.combinations(unique_items, itemset_len))
        condidate_itemsets += combs
    condidate_itemsets = np.array(condidate_itemsets, dtype=tuple)

    # find frquent itemsets
    freq_itemsets = []
    infreq_itemsets = []
    for itemset in condidate_itemsets:
        if itemset in tran_combs_count_dict:
            count = tran_combs_count_dict[itemset]
        else:
            count = 0
        support = count / total_num_tran
        if support >= minsup:
            freq_itemsets.append(itemset)
        else:
            infreq_itemsets.append(itemset)
            # set(a).issubset(b)
    
    print(freq_itemsets)
    print(len(freq_itemsets))
    
    # unique_item_count_dict = dict(zip(unique_items_counts[0], unique_items_counts[1]))
        
apriori(0.15, 0, 0, "task1.csv")