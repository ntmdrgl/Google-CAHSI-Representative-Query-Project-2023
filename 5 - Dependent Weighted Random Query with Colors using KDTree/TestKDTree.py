# -*- coding: utf-8 -*-
"""
Created on: November, 2023
Authors: Nathaniel Madrigal, Alexander Madrigal
"""

import KDTree
import numpy as np
import math
import time


input_size = 10000
num_dim = 10
rng = np.random.RandomState(0)
dataset = rng.random_sample((input_size, num_dim)).tolist() # create dataset_size points in num_dim dimensions

num_colors = 10
color_weight_dict = dict()
for i in range(1, num_colors + 1):
    color_weight_dict[str(i)] = 1000 * (0.5 * math.exp(-0.5 * i))

for i, point in enumerate(dataset):
    colored_point = (np.random.randint(1, num_colors), point)
    dataset[i] = colored_point
    
# dataset now contains a list of tuples
# the first element in the tuple is the color, the second is the list of dimensional coordinates

tree = KDTree.KDTree(dataset, color_weight_dict)

print(tree.root.color, tree.root.coord)