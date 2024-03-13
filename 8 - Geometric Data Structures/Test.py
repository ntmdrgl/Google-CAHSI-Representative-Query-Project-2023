# -*- coding: utf-8 -*-
"""
Created on: March 12, 2023
Authors: Nathaniel Madrigal, Alexander Madrigal

"""

import KdTree
import RangeTree
import numpy as np
from matplotlib import pyplot as plt
import math
import time
import random

input_size = 1000
num_dim = 2
dataset = np.random.default_rng().random((input_size, num_dim)).tolist()
num_colors = 20
num_queries = 100

# round each coodinate of point
for i in range(input_size):
    for j in range(len(dataset[i])):
        dataset[i][j] = round(dataset[i][j], 2)
     # add color to end of point
    dataset[i].append(i % num_colors + 1)
    
# generate dictionary of weights for colors
color_weight_dict = dict()
color_weight_list = list()
for i in range(1, num_colors + 1):
    weight_func = i    
       
    color_weight_dict[i] = weight_func
    color_weight_list.append(weight_func)   

# generate a set of queries to be used by data structure
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

print("Input size:", input_size)
print("Dimensions:", num_dim)
print("Colors:", num_colors)
print("Queries per tree:", num_queries, "\n")

# print weights
plt.bar(range(1, num_colors + 1), color_weight_list, color='blue')
plt.title('Weights of colors')
plt.xlabel('Color')
plt.ylabel('Weight')
plt.show()

def print_freqs_graph(color_samples, string):
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
    plt.title(f"Frequencies of colors from {string}")
    plt.xlabel('Color')
    plt.ylabel('Frequency')
    plt.show()

# build and query Kd-Tree
print("Building and Querying Kd-Tree...") 
t_start = time.time_ns()
tree = KdTree.KdTree(dataset, color_weight_dict)
t_end = time.time_ns()
print(f"Build time: {(t_end - t_start) / (10 ** 9)} seconds")

num_valid_samples = 0
color_samples = list()
t_sum = 0
for it, query_range in enumerate(query_ranges):
    min_point = query_range[0]
    max_point = query_range[1]
    
    t_start = time.time_ns()
    rand_sample = tree.query_random_sample(min_point, max_point)
    t_end = time.time_ns()
    t_sum += t_end - t_start
    
    if rand_sample is not None:
        color_samples.append(rand_sample.color)
        num_valid_samples += 1
t_avg = t_sum / num_queries
print(f"Average Query time: {(t_avg) / (10 ** 6)} miliseconds\n")
print_freqs_graph(color_samples, "Kd-Tree")

# build and query Range Tree
print("Building and Querying Range Tree...") 
t_start = time.time_ns()
tree = RangeTree.RangeTree(dataset, color_weight_dict)
t_end = time.time_ns()
print(f"Build time: {(t_end - t_start) / (10 ** 9)} seconds")

num_valid_samples = 0
color_samples = list()
t_sum = 0
for it, query_range in enumerate(query_ranges):
    min_point = query_range[0]
    max_point = query_range[1]
    
    t_start = time.time_ns()
    rand_sample = tree.query_random_sample(min_point, max_point)
    t_end = time.time_ns()
    t_sum += t_end - t_start
    
    if rand_sample is not None:
        color_samples.append(rand_sample.color)
        num_valid_samples += 1
t_avg = t_sum / num_queries
print(f"Average Query time: {(t_avg) / (10 ** 6)} miliseconds")
print_freqs_graph(color_samples, "Range Tree")