# -*- coding: utf-8 -*-
"""
Created on February 7, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal

"""
import OrthantSearchTree as OST
import numpy as np
import math
import time
import random

input_size = 10000
num_dim = 6
rng = np.random.default_rng()
dataset = rng.random((input_size, num_dim)).tolist() # create dataset_size points in num_dim dimensions
num_colors = 10

print('Input size:', len(dataset))
print('Number of dimensions:', num_dim)
print('Number of colors:', num_colors, '\n')

color_weight_dict = dict()
color_weight_list = list()
for i in range(1, num_colors + 1):
    color_weight_dict[i] = 1000 * (0.5 * math.exp(-0.5 * i))
    color_weight_list.append(1000 * (0.5 * math.exp(-0.5 * i))) 

for i, point in enumerate(dataset):
    dataset[i].append(np.random.randint(1, num_colors))
    
# build tree       
t_start = time.time_ns()
tree = OST.OrthantSearchTree(dataset, color_weight_dict) 
t_end = time.time_ns()
print(f"Build time: {(t_end - t_start) / (10 ** 6)} miliseconds\n") 

# query num_iterations times and count the colors of query results
num_iterations = 10000
color_counts = [0] * num_colors
fail_count = 0
x = list()
y = list()
colors = list()
t_sum = 0
for i in range(num_iterations):
    orthant = [random.random()] * (num_dim // 2)
    t_start = time.time_ns()
    random_node = tree.query_random_sample(orthant)
    t_end = time.time_ns()
    t_sum = t_sum + (t_end - t_start)
    
    if random_node is not None:
        color_counts[random_node.color - 1] += 1
        # data for plot
        x.append(random_node.coords[0])
        y.append(random_node.coords[1])
        colors.append(random_node.color)
    else:
        fail_count += 1

print(f"Avg query time ({num_iterations} trials): {(t_sum / (10 ** 6)) / num_iterations} miliseconds")
print(f'Success rate: {((num_iterations - fail_count) / num_iterations) * 100} %\n')