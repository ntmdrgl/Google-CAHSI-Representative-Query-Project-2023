# -*- coding: utf-8 -*-
"""
Created on February 7, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal

"""
import RectangularSearchTree_Old as RSTree
from matplotlib import pyplot as plt
import random
import math
import time
import json

import os
import sys
import psutil
from memory_profiler import profile

# def process_memory():
#     process = psutil.Process(os.getpid())
#     mem_info = process.memory_info()
#     return mem_info.rss

# @profile
# def my_build(dataset, color_weight_dict, x_const):
#     tree = RSTree.RectangularSearchTree(dataset, color_weight_dict, x_const)
#     return tree

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

# take arguments from dictionary and covert to list
dataset = list()
city_to_count = dict()
city_to_color = dict()
color_to_city = dict()
city_num = 1
for d in data:
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
        
    dataset.append([x, y, city_to_color[city]])
        
    
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
num_colors = len(color_to_city)
num_queries = 100

sub_dataset_size = 5
sub_dataset = list()
for i in range(sub_dataset_size):
    sub_dataset.append(dataset.pop(random.randint(0, len(dataset)-1)))    
print(sub_dataset)

# generate a set of queries to be used by data structure
query_ranges = list() # list of lists of type [x_range, y_range]
for it in range(num_queries):
    x_range = [round(random.random(),3), round(random.random(),3)]  
    y_range = [round(random.random(),3), round(random.random(),3)]
    if x_range[0] > x_range[1]:
        (x_range[0], x_range[1]) = (x_range[1], x_range[0])
    if y_range[0] > y_range[1]:
        (y_range[0], y_range[1]) = (y_range[1], y_range[0])
    query_ranges.append([x_range, y_range])

# generate dictionary of weights for colors
color_weight_dict = dict()
color_weight_list = list()
for i in range(1, num_colors + 1):
    # weight_func = city_to_count[color_to_city[i]]
    weight_func = i    
       
    color_weight_dict[i] = weight_func
    color_weight_list.append(weight_func)   

print("Input size:", input_size)
print("Subset size:", sub_dataset_size)
print("Dimensions:", num_dim)
print("Colors:", num_colors)
print("Queries per tree:", num_queries, "\n")

# build tree
print("Building tree: \n") 
x_const = math.sqrt(input_size)

t_start = time.time_ns()
# mem_before = process_memory()
tree = RSTree.RectangularSearchTree(sub_dataset, color_weight_dict, x_const)
# mem_after = process_memory()
t_end = time.time_ns()
print(f"Build time: {(t_end - t_start) / (10 ** 9)} seconds")
# print(f"Space consumed: {mem_after - mem_before}\n")

# query tree
print("Querying:")
num_valid_samples = 0
color_samples = list()
t_sum = 0
for it, query_range in enumerate(query_ranges):
    x_range = query_range[0]
    y_range = query_range[1]
    
    t_start = time.time_ns()
    rand_color_sample = tree.report_colors(x_range, y_range)
    t_end = time.time_ns()
    t_sum += t_end - t_start
    
    if rand_color_sample is not None:
        color_samples.append(rand_color_sample)
        num_valid_samples += 1
t_avg = t_sum / num_queries
    
print(f"Average Query time: {(t_avg) / (10 ** 6)} miliseconds")

print(f"Light %: {round(tree.light_count / (tree.light_count + tree.heavy_count), 3) * 100}\n")

# plt.bar(range(1, num_colors + 1), color_weight_list, color='blue')
# plt.title('Weights of colors')
# plt.xlabel('Color')
# plt.ylabel('Weight')
# plt.show()