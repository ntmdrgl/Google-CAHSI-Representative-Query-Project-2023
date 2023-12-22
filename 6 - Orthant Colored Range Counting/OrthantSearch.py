# -*- coding: utf-8 -*-
"""
Created on: November 29, 2023
Authors: Nathaniel Madrigal, Alexander Madrigal

In 2 dimensions:
- Each point is represented by (x, y)
- The query range is defined with an Orthant rooted at point (a, b)
    - Covers region [-inf, a] x [-inf, b]

Objective:
- Build data structure to quickly return a random colored point from points intersecting Orthant query range
    - color returns in probability proportional to weight of color

"""

import KDTree
import numpy as np
import random
import math
import time
from matplotlib import pyplot as plt

input_size = 10000
num_dim = 2
num_colors = 10

# create input_size points in num_dim dimensions
rng = np.random.default_rng()
dataset = rng.random((input_size, num_dim)).tolist()

# create a dictionary containing weights of colors
color_weight_dict = dict()
color_weight_list = list()
for i in range(1, num_colors + 1):
    color_weight_dict[i] = 1000 * (0.5 * math.exp(-0.5 * i))
    color_weight_list.append(1000 * (0.5 * math.exp(-0.5 * i))) 


# transform dataset of points (lists) with color as last element in list
for idx in range(len(dataset)):
    color = np.random.randint(1, num_colors)
    dataset[idx].append(color)

# build tree       
tree = KDTree.KDTree(dataset, color_weight_dict)    

# query num_iterations times and count the colors of query results
num_iterations = 1000
color_counts = [0] * num_colors
orthant = [random.random(), random.random()]
for i in range(num_iterations):        
    random_node = tree.query_random_node(orthant)
    if random_node is not None:
        color_counts[random_node.color - 1] += 1
    
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