# -*- coding: utf-8 -*-
"""
Created on March 6, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal
"""

import RectangularSearchTree_Old as RSTree
from matplotlib import pyplot as plt
import pandas as pd
import random
import math
import time
import os


# change path to open datasets directory
path = os.path.realpath(__file__) 
dir = os.path.dirname(path) 
dir = dir.replace('7 - 2D Rectangular Query with Orthant Data Structures', 'Datasets') 
os.chdir(dir) 

# extract data from 2d_dataset.txt
print("Extracting txt file...")
data = pd.read_csv('2d_dataset.txt', sep=',', header=None, names=['x', 'y'], low_memory=False)
dataframe = pd.DataFrame(data)
dataset = dataframe.to_numpy().tolist()
    # original colors assigned to dataset:
    # color 0: 1-1725
    # color 1: 1726-39805
    # color 2: 39806-334533
    # color 3: 334534-1039726
    # color 4: 1039727-4110608

for it, point in enumerate(dataset):
    if it < 1725:
        dataset[it].append(1)
    elif it < 39805:
        dataset[it].append(2)
    elif it < 334533:
        dataset[it].append(3)
    elif it < 1039726:
        dataset[it].append(4)
    else:
        dataset[it].append(5)

input_size = len(dataset)
num_dim = len(dataset[0]) - 1
num_colors = 5

# normalize data (highest value for x and y is 100000.0)
# assign colors from 1 to num_colors to dataset's points
print("Normalizing data...")
for it, point in enumerate(dataset):
    point[0] /= 100000
    point[1] /= 100000
    point.append(it % num_colors + 1)

# generate dictionary of weights for colors
color_freq_list = [1725, 38080, 294728, 705193, 3070882]
color_weight_dict = dict()
color_weight_list = list()
for i in range(1, num_colors + 1):
    color_weight_dict[i] = (len(dataset) - (color_freq_list[i - 1])) / len(dataset)
    color_weight_list.append((len(dataset) - (color_freq_list[i - 1])) / len(dataset))   

# generate a set of queries to be used by data structure
print("Generating query ranges...")
num_queries = 1000
query_ranges = list() # list of ranges of type [min_point, max_point]
for it in range(num_queries):
    min_point = list()
    max_point = list()
    for i in range(num_dim):
        axis_range = [round(random.random(),3), round(random.random(),3)]
        if axis_range[0] > axis_range[1]:
            (axis_range[0], axis_range[1]) = (axis_range[1], axis_range[0])
        min_point.append(axis_range[0])
        max_point.append(axis_range[1])
    query_ranges.append([min_point, max_point])

# create sub dataset
print("Generating subset dataset...\n")
sub_dataset_size = 200
random.shuffle(dataset)
sub_dataset = list()
for i in range(sub_dataset_size):
    # sub_dataset.append(dataset.pop(random.randint(0, len(dataset)-1)))
    sub_dataset.append(dataset.pop())    

print("Input size:", input_size)
print("Dimensions:", num_dim)
print("Colors:", num_colors)
print("Queries per tree:", num_queries)
print("Subset size:", sub_dataset_size, "\n")

# build tree
print("Building tree...") 
x_const = 2
t_start = time.time_ns()
tree = RSTree.RSTree(sub_dataset, color_weight_dict, x_const)
t_end = time.time_ns()
print(f"Build time: {(t_end - t_start) / (10 ** 9)} seconds\n")

heavy_nodes = list()
avg_query_times = list()
for i in range(0, 2): # 0, 3
    if i == 0:
        heavy_nodes.append(0)
        avg_query_times.append(0)
        continue
    x_const_mult = 1
    tree.x_const = i * x_const_mult
    
    # query tree
    print("Querying...")
    num_valid_samples = 0
    color_samples = list()
    canonical_node_counts = list()
    sum_heavy = 0
    sum_total = 0
    t_sum = 0
    allCorrect = True
    for it, query_range in enumerate(query_ranges):
        min_point = query_range[0]
        max_point = query_range[1]
        x_range = [min_point[0], max_point[0]]
        y_range = [min_point[1], max_point[1]]
        
        
        t_start = time.time_ns()
        # rand_sample = tree.query_random_sample(x_range, y_range)
        rand_sample = tree.query_random_sample(min_point, max_point)
        
        t_end = time.time_ns()
        t_sum += t_end - t_start
        
        if tree.avg_count is not None:
            canonical_node_counts.append(tree.avg_count)
        
        if rand_sample is not None:
            # if not (x_range[0] < rand_sample.orig_coords[0] < x_range[1] and y_range[0] < rand_sample.orig_coords[1] < y_range[1]):
            if not (min_point[0] < rand_sample.original_point[0] < max_point[0] and min_point[1] < rand_sample.original_point[1] < max_point[1]):
                allCorrect = False
                # print("INCORRECT", rand_sample.orig_coords, x_range, y_range)
                print("INCORRECT", rand_sample.original_point, x_range, y_range)
            color_samples.append(rand_sample.color)
            num_valid_samples += 1
            sum_heavy += tree.heavy_count
            sum_total += tree.heavy_count + tree.light_count
    
    if allCorrect:
        print("All samples inside of Query Ranges!")
    
    t_avg = t_sum / num_queries
    print(f"Average Query time: {(t_avg) / (10 ** 6)} miliseconds")
    print(f"Returned samples: {num_valid_samples}")
    if len(canonical_node_counts) != 0:
        print(f"Average canonical node size: {sum(canonical_node_counts) / len(canonical_node_counts)}")
    else:
        print("Average canonical node size: Undefined")
    print(f"X Const: {tree.x_const}")
    print(f"Heavy nodes: {sum_heavy}")
    print(f"Light+Heavy nodes: {sum_total}\n")
    if not sum_total == 0:
        heavy_nodes.append(sum_heavy / sum_total)
    else:
        heavy_nodes.append(0)
    avg_query_times.append((t_avg) / (10 ** 6))
    
for it in range(5):
    color_freq_list[it] /= len(dataset)
plt.bar(range(1, num_colors + 1), color_freq_list, color='green')
plt.title('Frequencies of colors in dataset')
plt.xlabel('Color')
plt.ylabel('Frequencies')
plt.show()
    
plt.bar(range(1, num_colors + 1), color_weight_list, color='blue')
plt.title('Weights of colors')
plt.xlabel('Color')
plt.ylabel('Weight')
plt.show()

color_counts = [0] * num_colors
for it, color in enumerate(color_samples):
    idx = color - 1
    color_counts[idx] += 1

color_freqs = [0] * num_colors
for it, count in enumerate(color_counts):
    if num_valid_samples == 0:
        color_freqs[it] = 0
    else:
        color_freqs[it] = count / num_valid_samples
        
plt.bar(range(1, num_colors + 1), color_freqs, color='orange')
plt.title("Frequencies of colors from random samples")
plt.xlabel('Color')
plt.ylabel('Frequency')
plt.show()

# print("color freq in dataset:")
# for i in color_freq_list:
#     print(i)

# print("\ncolor weights:")
# for i in color_weight_list:
#     print(i)

# print("\ncolor freq from samples:")
# for i in color_freqs:
#     print(i)

# xs = list()
# for i in range(0, len(heavy_nodes)):
#     xs.append(i * x_const_mult)
# plt.bar(xs, heavy_nodes, color='green')
# plt.title("Heavy nodes vs. X Const")
# plt.xlabel('X Const')
# plt.ylabel('Heavy Node (%)')
# plt.show()

# plt.bar(range(0, len(avg_query_times)), avg_query_times, color='turquoise')
# plt.title("Query time vs. X Const")
# plt.xlabel('X Const')
# plt.ylabel('Average Query Time (ms)')
# plt.show()