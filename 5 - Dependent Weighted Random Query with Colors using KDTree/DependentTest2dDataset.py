# -*- coding: utf-8 -*-
"""
Created on January 23, 2024
Authors: Alexander Madrigal and Nathaniel Madrigal
"""

import KDTree2D
import numpy as np
import random
import pandas as pd
import math
import time
from matplotlib import pyplot as plt
import os

# change path to open datasets directory
path = os.path.realpath(__file__) 
dir = os.path.dirname(path) 
dir = dir.replace('5 - Dependent Weighted Random Query with Colors using KDTree', 'Datasets') 
os.chdir(dir) 

data = pd.read_csv('2d_dataset.txt', sep=',', header=None, names=['x', 'y'], low_memory=False)

dataframe = pd.DataFrame(data)

dataset = dataframe.to_numpy().tolist()
# color 0: 1-1725
# color 1: 1726-39805
# color 2: 39806-334533
# color 3: 334534-1039726
# color 4: 1039727-4110608

x_map = list()
y_map = list()
colors_map = list()
for it, point in enumerate(dataset):
    if it < 1725:
        dataset[it].append(1)
    elif it < 39805:
        dataset[it].append(2)
    elif it < 334533:
        dataset[it].append(3)
    elif it < 1039726:
        dataset[it].append(4)
        # x_map.append(point[0])
        # y_map.append(point[1])
        # colors_map.append(point[2])
    else:
        dataset[it].append(5)
        
    # x_map.append(point[0])
    # y_map.append(point[1])
    # colors_map.append(point[2])

num_colors = 5

print('Input size:', len(dataset))
print('Number of dimensions:', 2)
print('Number of colors:', num_colors, '\n')

# create a dictionary containing weights of colors
color_freq_list = [1725, 38080, 294728, 705193, 3070882]
color_weight_dict = dict()
color_weight_list = list()
for i in range(1, num_colors + 1):
    color_weight_dict[str(i)] = (len(dataset) - (color_freq_list[i - 1])) / len(dataset)
    color_weight_list.append((len(dataset) - (color_freq_list[i - 1])) / len(dataset)) 

for it in range(5):
    color_freq_list[it] /= len(dataset)

# create sub dataset
sub_dataset = list()
for i in range(10000):
    sub_dataset.append(dataset.pop(random.randint(0, len(dataset)-1)))    

# sub_dataset = dataset

# build tree       
t_start = time.time_ns()
tree = KDTree2D.KDTree(sub_dataset, color_weight_dict) 
t_end = time.time_ns()

print(f"Build time: {(t_end - t_start) / (10 ** 9)} seconds\n")   

# query num_iterations times and count the colors of query results
num_iterations = 10000
color_counts = [0] * num_colors
fail_count = 0
x = list()
y = list()
colors = list()
t_sum = 0
for i in range(num_iterations):
    min_point = list()
    max_point = list()
    for i in range(2):
        min_interval = round((0.975 * random.random()) * 100000, 3)
        max_interval = round((min_interval) + (0.025 * 100000), 3)
        if min_interval > max_interval:
            (min_interval, max_interval) = (max_interval, min_interval)
        min_point.append(min_interval)
        max_point.append(max_interval)
        
    t_start = time.time_ns()
    random_node = tree.query_random_sample(min_point, max_point)
    t_end = time.time_ns()
    t_sum = t_sum + (t_end - t_start)
    
    if random_node is not None:
        color_counts[int(random_node.color) - 1] += 1
        # data for plot
        x.append(random_node.coord[0])
        y.append(random_node.coord[1])
        colors.append(int(random_node.color))
    else:
        fail_count += 1

print(f"Avg query time ({num_iterations} trials): {(t_sum / (10 ** 6)) / num_iterations} miliseconds")
print(f'Success rate: {((num_iterations - fail_count) / num_iterations) * 100} %\n')

# find frequencies of colors
color_freqs = [None] * num_colors
for i in range(num_colors):
    if (num_iterations - fail_count) != 0:
        color_freqs[i] = color_counts[i] / (num_iterations - fail_count)
    else: 
        color_freqs[i] = 0

plt.bar(range(1, num_colors + 1), color_freq_list, color='green')
plt.title('Frequencies of colors in dataset')
plt.xlabel('Color')
plt.ylabel('Frequencies')
plt.show()

sample_color_sum = 0
for count in tree.color_counts:
    sample_color_sum += count
sample_color_freq = list()
for count in tree.color_counts:
    sample_color_freq.append(count / sample_color_sum)
plt.bar(range(1, num_colors + 1), sample_color_freq, color='yellow')
plt.title('Frequencies of colors in sampled canonical nodes (atleast one of color)')
plt.xlabel('Color')
plt.ylabel('Frequencies')
plt.show()


plt.bar(range(1, num_colors + 1), color_weight_list, color='blue')
plt.title('Weights of colors')
plt.xlabel('Color')
plt.ylabel('Weight')
plt.show()

plt.bar(range(1, num_colors + 1), color_freqs, color='orange')
plt.title('Frequencies of colors from random query sampling')
plt.xlabel('Color')
plt.ylabel('Frequency')
plt.show()

plt.scatter(x, y, c=colors)
plt.title('Plot of successful query samples')
plt.colorbar()
plt.show()

print("color freq in dataset:")
for i in color_freq_list:
    print(i)

print("\ncolor weights:")
for i in color_weight_list:
    print(i)

print("\ncolor freq from samples:")
for i in color_freqs:
    print(i)

# x.append(100000)
# y.append(100000)
# colors.append(100)
# sizes = [5] * len(x)
# plt.scatter(x, y, s=sizes, c=colors)
# plt.title('Plot of successful query samples')
# plt.colorbar()
# plt.show()

# sizes_map = [5] * len(x_map)
# plt.scatter(x_map, y_map, s=sizes_map, c=colors_map, alpha=0.2)
# plt.title('Plot of dataset')
# plt.colorbar()
# plt.show()
