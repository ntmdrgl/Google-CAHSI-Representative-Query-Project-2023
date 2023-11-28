# -*- coding: utf-8 -*-
"""
Created on: November 16, 2023
Authors: Nathaniel Madrigal, Alexander Madrigal
"""

import KDTree
import numpy as np
import pandas as pd
import math
import time
from matplotlib import pyplot as plt


input_size = 40000
num_dim = 6
rng = np.random.default_rng()
dataset = rng.random((input_size, num_dim)).tolist() # create dataset_size points in num_dim dimensions

num_colors = 10
color_weight_dict = dict()
color_weight_list = list()
for i in range(1, num_colors + 1):
    color_weight_dict[str(i)] = 1000 * (0.5 * math.exp(-0.5 * i))
    color_weight_list.append(1000 * (0.5 * math.exp(-0.5 * i))) 

for i, point in enumerate(dataset):
    colored_point = (np.random.randint(1, num_colors), point)
    dataset[i] = colored_point
    
t = time.time_ns()
tree = KDTree.KDTree(dataset, color_weight_dict)
print('Build time:', ((time.time_ns() - t) / (10 ** 6)), 'ms')

# initialize counts of colors to 0
color_counts = list()
for i in range(num_colors):
    color_counts.append(0)

num_iterations = 200
        
t_sum = 0
none_count = 0
for i in range(num_iterations):
    # create query range
    min_coords = (0.7 - 0) * rng.random((num_dim, )) + 0
    max_coords = min_coords + 0.30
    min_coords = min_coords.tolist()
    max_coords = max_coords.tolist()

    # query random node
    t_start = time.time_ns()
    random_node = tree.query_random_sample(min_coords, max_coords)
    t_end = time.time_ns()
    t_sum = t_sum + (t_end - t_start)
    
    if random_node is None:
        none_count = none_count + 1
        continue
    
    # add frequency of random node's color
    color_counts[int(random_node.color) - 1] = color_counts[int(random_node.color) - 1] + 1
print(f"Avg query time ({num_iterations} trials): {(t_sum / (10 ** 6)) / num_iterations} ms")

print('Success rate:', (num_iterations - none_count) / num_iterations)

# find frequencies of colors
color_freqs = [None] * num_colors
for i in range(num_colors):
    color_freqs[i] = color_counts[i] / num_iterations

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