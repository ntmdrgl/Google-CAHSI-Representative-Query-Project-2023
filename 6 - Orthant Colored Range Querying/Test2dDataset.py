# -*- coding: utf-8 -*-
"""
Created on January 23, 2024
Authors: Alexander Madrigal and Nathaniel Madrigal
"""

import KDTree
import numpy as np
import random
import pandas as pd
import math
import time
from matplotlib import pyplot as plt

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
        dataset[it].append(0)
    elif it < 39805:
        dataset[it].append(1)
    elif it < 334533:
        dataset[it].append(2)
    elif it < 1039726:
        dataset[it].append(3)
    else:
        dataset[it].append(4)
        
    x_map.append(point[0])
    y_map.append(point[1])
    colors_map.append(point[2])
    
num_colors = 5

# create a dictionary containing weights of colors
color_freq_list = [1725, 38080, 294728, 705193, 3070882]
color_weight_dict = dict()
color_weight_list = list()
for i in range(num_colors):
    color_weight_dict[i] = len(dataset) - (color_freq_list[i])
    color_weight_list.append(len(dataset) - (color_freq_list[i])) 

for it in range(5):
    color_freq_list[it] /= len(dataset)

print('Start building tree')

# build tree       
tree = KDTree.KDTree(dataset, color_weight_dict)    

print('Finished building tree')
print('Start querying')

# query num_iterations times and count the colors of query results
num_iterations = 10000
color_counts = [0] * num_colors
fail_count = 0
x = list()
y = list()
colors = list()
for i in range(num_iterations):
    orthant = [random.random() * 100000, random.random() * 100000]        
    random_node = tree.query_random_node(orthant)
    if random_node is not None:
        color_counts[random_node.color - 1] += 1
        # data for plot
        x.append(random_node.coords[0])
        y.append(random_node.coords[1])
        colors.append(random_node.color)
    else:
        fail_count += 1

print('Finished querying')

print('Success rate:', (num_iterations - fail_count) / num_iterations, '(', num_iterations - fail_count, ') queries')

# find frequencies of colors
color_freqs = [None] * num_colors
for i in range(num_colors):
    color_freqs[i] = color_counts[i] / (num_iterations - fail_count)

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

plt.bar(range(1, num_colors + 1), color_freqs, color='orange')
plt.title('Frequencies of colors from random query sampling')
plt.xlabel('Color')
plt.ylabel('Frequency')
plt.show()

plt.scatter(x, y, c=colors)
plt.title('Plot of successful query samples')
plt.colorbar()
plt.show()

x.append(100000)
y.append(100000)
colors.append(100)
sizes = [5] * len(x)
plt.scatter(x, y, s=sizes, c=colors)
plt.title('Plot of successful query samples')
plt.colorbar()
plt.show()

sizes_map = [5] * len(x_map)
plt.scatter(x_map, y_map, s=sizes_map, c=colors_map, alpha=0.2)
plt.title('Plot of dataset')
plt.colorbar()
plt.show()
