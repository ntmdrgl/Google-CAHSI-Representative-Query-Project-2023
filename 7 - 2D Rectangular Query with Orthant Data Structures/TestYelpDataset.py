# -*- coding: utf-8 -*-
"""
Created on February 7, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal

"""
# import RectangularSearchTree as RSTree
import RectangularSearchTree_Old as RSTree
from matplotlib import pyplot as plt
import numpy as np
import random
import math
import time
import json

import os
import sys
import psutil
# from memory_profiler import profile

# change path to open datasets directory
path = os.path.realpath(__file__) 
dir = os.path.dirname(path) 
dir = dir.replace('7 - 2D Rectangular Query with Orthant Data Structures', 'Datasets') 
os.chdir(dir) 

# extract dictionaries from json file
print("Extracting json file...")
data = []
with open('yelp_academic_dataset_business.json', 'r', encoding="utf8") as file:
    for line in file:
        data.append(json.loads(line))

num_colors = 1400

# take arguments from dictionary and covert to list
dataset = list()
city_to_count = dict()
city_to_color = dict()
color_to_city = dict()
city_num = 1
for it, d in enumerate(data):
    x = d.get("latitude")
    y = d.get("longitude")
    city = d.get("city")
    
    if city not in city_to_color.keys():
        city_to_count[city] = 1
        city_to_color[city] = city_num
        color_to_city[city_num] = city
        city_num += 1
    else:
        city_to_count[city] += 1
        
    # dataset.append([x, y, city_to_color[city]])
    dataset.append([x, y, it % num_colors + 1])   
    
# normalize points
print("Normalizing data...\n")
x_min = 27.555127
x_max = 53.6791969
y_min = -120.095137
y_max = -73.2004570502
for point in dataset:
    point[0] = (point[0] - x_min) / (x_max - x_min)
    point[1] = (point[1] - y_min) / (y_max - y_min)
    
input_size = len(dataset)
num_dim = 2
# num_colors = len(color_to_city)
num_queries = 1000
sub_dataset_size = 3000

# create sub dataset
sub_dataset = list()
for i in range(sub_dataset_size):
    sub_dataset.append(dataset.pop(random.randint(0, len(dataset)-1)))    

# # Simulated dataset
# input_size = 1000
# num_dim = 2
# dataset = np.random.default_rng().random((input_size, num_dim)).tolist()
# num_colors = 20
# num_queries = 100

# # Add colors to simulated dataset
# for point in dataset:
#     point.append(i % num_colors + 1)
# sub_dataset = dataset
# sub_dataset_size = input_size

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
    
# generate dictionary of weights for colors
color_weight_dict = dict()
color_weight_list = list()
for i in range(1, num_colors + 1):
    # weight_func = city_to_count[color_to_city[i]]
    weight_func = 1    
       
    color_weight_dict[i] = weight_func
    color_weight_list.append(weight_func)   

print("Input size:", input_size)
print("Subset size:", sub_dataset_size)
print("Dimensions:", num_dim)
print("Colors:", num_colors)
print("Queries per tree:", num_queries, "\n")

# build tree
print("Building tree...") 
x_const = 2
t_start = time.time_ns()
tree = RSTree.RSTree(sub_dataset, color_weight_dict, x_const)
t_end = time.time_ns()
print(f"Build time: {(t_end - t_start) / (10 ** 9)} seconds\n")

heavy_nodes = list()
avg_query_times = list()
for i in range(0, 11):
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
    for it, query_range in enumerate(query_ranges):
        min_point = query_range[0]
        max_point = query_range[1]
        x_range = [min_point[0], max_point[0]]
        y_range = [min_point[1], max_point[1]]
        
        
        t_start = time.time_ns()
        # rand_sample = tree.query_random_sample(min_point, max_point)
        rand_sample = tree.query_random_sample(x_range, y_range)
        t_end = time.time_ns()
        t_sum += t_end - t_start
        
        if tree.avg_count is not None:
            canonical_node_counts.append(tree.avg_count)
        
        if rand_sample is not None:
            allCorrect = True
            if not (x_range[0] < rand_sample.orig_coords[0] < x_range[1] and y_range[0] < rand_sample.orig_coords[1] < y_range[1]):
            # if not (min_point[0] < rand_sample.original_point[0] < max_point[0] and min_point[1] < rand_sample.original_point[1] < max_point[1]):
                allCorrect = True
                print("INCORRECT, outside of query range", rand_sample.orig_coords, x_range, y_range)
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
    heavy_nodes.append(sum_heavy / sum_total)
    avg_query_times.append((t_avg) / (10 ** 6))
    
# plt.bar(range(1, num_colors + 1), color_weight_list, color='blue')
# plt.title('Weights of colors')
# plt.xlabel('Color')
# plt.ylabel('Weight')
# plt.show()

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

xs = list()
for i in range(0, len(heavy_nodes)):
    xs.append(i * x_const_mult)
plt.bar(xs, heavy_nodes, color='green')
plt.title("Heavy nodes vs. X Const")
plt.xlabel('X Const')
plt.ylabel('Heavy Node (%)')
plt.show()

plt.bar(range(0, len(avg_query_times)), avg_query_times, color='turquoise')
plt.title("Query time vs. X Const")
plt.xlabel('X Const')
plt.ylabel('Average Query Time (ms)')
plt.show()