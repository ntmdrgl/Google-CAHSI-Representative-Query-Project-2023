# -*- coding: utf-8 -*-
"""
Created on: November, 2023
Authors: Nathaniel Madrigal, Alexander Madrigal
"""

import KDTree
import numpy as np
from matplotlib import pyplot as plt
import math
import time


input_size = 40000
num_dim = 6
rng = np.random.default_rng()
dataset = rng.random((input_size, num_dim)).tolist() # create dataset_size points in num_dim dimensions

num_colors = 10
color_weight_dict = dict()
for i in range(1, num_colors + 1):
    color_weight_dict[str(i)] = 1000 * (0.5 * math.exp(-0.5 * i))

for i, point in enumerate(dataset):
    colored_point = (np.random.randint(1, num_colors), point)
    dataset[i] = colored_point
    
# dataset now contains a list of tuples
# the first element in the tuple is the color, the second is the list of dimensional coordinates

min_coords = ((1 - 0) * rng.random((num_dim, )) + 0).tolist()
max_coords = ((1 - 0) * rng.random((num_dim, )) + 0).tolist()
for dim in range(num_dim):
    if min_coords[dim] > max_coords[dim]:
        (min_coords[dim], max_coords[dim]) = (max_coords[dim], min_coords[dim])

# print('avg distance:', distance)
t = time.time_ns()
tree = KDTree.KDTree(dataset, color_weight_dict)
print('Build time:', ((time.time_ns() - t) / (10 ** 6)), 'ms')

# initialize counts of colors to 0
color_counts = list()
for i in range(num_colors):
    color_counts.append(0)

num_iterations = 100
        
t_sum = 0
for i in range(num_iterations):
    # create query range
    min_coords = (0.70 - 0) * rng.random((num_dim, )) + 0
    max_coords = min_coords + 0.30
    min_coords = min_coords.tolist()
    max_coords = max_coords.tolist()

    # query random node
    t_start = time.time_ns()
    random_node = tree.query_random_sample(min_coords, max_coords)
    t_end = time.time_ns()
    t_sum = t_sum + (t_end - t_start)
    
    if random_node is None:
        continue
    
    # add frequency of random node's color
    color_counts[int(random_node.color) - 1] = color_counts[int(random_node.color) - 1] + 1
print('Avg query time:', (t_sum / (10 ** 6)) / num_iterations, 'ms')

# find frequencies of colors
color_freqs = [None] * num_colors
for i in range(num_colors):
    color_freqs[i] = color_counts[i] / num_iterations

plt.bar(range(1, num_colors + 1), color_freqs, color='orange')
plt.title('Test 2: Frequencies of colors from random query sampling')
plt.xlabel('Color')
plt.ylabel('Frequency')
plt.show()