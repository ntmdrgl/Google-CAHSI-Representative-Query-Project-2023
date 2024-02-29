# -*- coding: utf-8 -*-
"""
Created on February 7, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal

"""
import RectangularSearchTree as RSTree
import OrthogonalSearchTree as OSTree
import MaxEmptyOrthTree as MEOTree
import numpy as np
import math
import time
import random

input_size = 10
num_dim = 2
rng = np.random.default_rng()
dataset = rng.random((input_size, num_dim)).tolist() # create dataset_size points in num_dim dimensions
num_colors = 1

print('Input size:', len(dataset))
print('Number of dimensions:', num_dim)
print('Number of colors:', num_colors, '\n')

color_weight_dict = dict()
color_weight_list = list()
for i in range(1, num_colors + 1):
    color_weight_dict[i] = 1000 * (0.5 * math.exp(-0.5 * i))
    color_weight_list.append(1000 * (0.5 * math.exp(-0.5 * i))) 

for i, point in enumerate(dataset):
    dataset[i].append(np.random.randint(1, num_colors + 1))
    
# build tree       
t_start = time.time_ns()
tree = OSTree.OrthogonalSearchTree(dataset, color_weight_dict) 
t_end = time.time_ns()
print(f"Build time: {(t_end - t_start) / (10 ** 6)} miliseconds\n") 

# query num_iterations times and count the colors of query results
num_iterations = 1
fail_count = 0

def find_subset(root):
    color_set = list()
    
    if root.left is None and root.right is None:
        return [root.color]
    
    if root.left is not None and root.right is not None:
        sub_left = find_subset(root.left)
        sub_right = find_subset(root.right)
        
        if sub_left:
            color_set += sub_left
        if sub_right:
            color_set += sub_right
    
    return color_set

t_sum = 0
for i in range(num_iterations):
    orthant = [random.random()] * num_dim
    t_start = time.time_ns()
    canonical_colors = tree.report_colors(orthant, False)
    t_end = time.time_ns()
    t_sum = t_sum + (t_end - t_start)
    
    if canonical_colors is not None:
        colors = list()
        for c in canonical_colors:
            colors += find_subset(c)
        print(colors)
    else:
        fail_count += 1


print(f"Avg query time ({num_iterations} trials): {(t_sum / (10 ** 6)) / num_iterations} miliseconds")
print(f'Success rate: {((num_iterations - fail_count) / num_iterations) * 100} %\n')