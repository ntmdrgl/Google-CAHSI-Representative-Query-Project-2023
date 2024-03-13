# -*- coding: utf-8 -*-
"""
Created on March 6, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal
"""

import RectangularSearchTree as RSTree
from matplotlib import pyplot as plt
import pandas as pd
import random
import math
import time

import os
import psutil
from memory_profiler import profile

# inner psutil function
def process_memory():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss

@profile
def my_build(dataset, color_weight_dict, x_const):
    tree = RSTree.RectangularSearchTree(dataset, color_weight_dict, x_const)
    return tree

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

input_size = len(dataset)
num_dim = len(dataset[0])
num_colors = 100

# normalize data (highest value for x and y is 100000.0)
# assign colors from 1 to num_colors to dataset's points
print("Normalizing data...\n")
for it, point in enumerate(dataset):
    point[0] /= 100000
    point[1] /= 100000
    point.append(it % num_colors + 1)

# generate a set of queries to be used by data structure
num_queries = 10
query_ranges = list() # list of lists of type [x_range, y_range]
for it in range(num_queries):
    x_range = [round(random.random(),3), round(random.random(),3)]  
    y_range = [round(random.random(),3), round(random.random(),3)]
    # x_range = [0, 1]
    # y_range = [0, 1]
    if x_range[0] > x_range[1]:
        (x_range[0], x_range[1]) = (x_range[1], x_range[0])
    if y_range[0] > y_range[1]:
        (y_range[0], y_range[1]) = (y_range[1], y_range[0])
    query_ranges.append([x_range, y_range])

# generate dictionary of weights for colors
color_weight_dict = dict()
color_weight_list = list()
for i in range(1, num_colors + 1):
    weight_func = i
       
    color_weight_dict[i] = weight_func
    color_weight_list.append(weight_func)    

print("Input size:", input_size)
print("Dimensions:", num_dim)
print("Colors:", num_colors)
print("Queries per tree:", num_queries, "\n")

for it in range(1, 4):
    sub_dataset = dataset[:10**it]
    # build tree
    print(f"Building tree (size:{10**it}): \n") 
    x_const = math.sqrt(input_size)
    
    t_start = time.time_ns()
    mem_before = process_memory()
    tree = my_build(sub_dataset, color_weight_dict, x_const)
    mem_after = process_memory()
    t_end = time.time_ns()
    print(f"Build time: {(t_end - t_start) / (10 ** 9)} seconds")
    print(f"Space consumed: {mem_after - mem_before}\n")
# query tree
# print("Querying...")
# num_valid_samples = 0
# color_samples = list()
# t_sum = 0
# for it, query_range in enumerate(query_ranges):
#     x_range = query_range[0]
#     y_range = query_range[1]
    
#     t_start = time.time_ns()
#     rand_color_sample = tree.report_colors(x_range, y_range)
#     t_end = time.time_ns()
#     t_sum += t_end - t_start
    
#     if rand_color_sample is not None:
#         color_samples.append(rand_color_sample)
#         num_valid_samples += 1
# t_avg = t_sum / num_queries
    
# print(f"Average Query time: {(t_avg) / (10 ** 6)} miliseconds")

# print(f"Light %: {round(tree.light_count / (tree.light_count + tree.heavy_count), 3) * 100}\n")

# print(tree.counts_in_queries)

# dataset_3 = dataset[:10000]
# t_start = time.time_ns()
# tree.transform_dataset(dataset_3, True, True)
# t_end = time.time_ns() 
# print(f"Transform time: {(t_end - t_start) / (10 ** 9)} seconds")