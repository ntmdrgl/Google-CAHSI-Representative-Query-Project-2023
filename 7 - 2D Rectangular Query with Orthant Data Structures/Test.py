# -*- coding: utf-8 -*-
"""
Created on February 7, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal

"""
import RectangularSearchTree as RSTree
import numpy as np
from matplotlib import pyplot as plt
import math
import time
import random

input_size = 50000
num_dim = 2
rng = np.random.default_rng()
dataset = rng.random((input_size, num_dim)).tolist() # create dataset_size points in num_dim dimensions
num_colors = 200
num_iterations = 100

for i in range(input_size):
    # round each coodinate of point
    for j in range(len(dataset[i])):
        dataset[i][j] = round(dataset[i][j], 2)
    # add color to end of point
    dataset[i].append(i % num_colors + 1)
    
print('Input size:', len(dataset))
print('Number of dimensions:', num_dim)
print('Number of colors:', num_colors, '\n')

color_weight_dict = dict()
color_weight_list = list()
avg_weight = 0
for i in range(1, num_colors + 1):
    weight_func = i
    # weight_func = 1000 * (0.05 * math.exp(-0.05 * i))
    
    avg_weight += weight_func    
    color_weight_dict[i] = weight_func
    color_weight_list.append(weight_func) 
avg_weight /= num_colors

# test multiple x constants on the datastructure
xs = list()
for i in range(1, 10):
    x_func = (i) * 0.1
    xs.append(x_func)

xs = [math.sqrt(input_size)]

build_times = list()
query_times = list()
light_percents = list()
first_iteration = True

for it, x_const in enumerate(xs):
    if len(xs) != 1:
        x_const *= avg_weight
    
    # build tree       
    t_start = time.time_ns()
    tree = RSTree.RectangularSearchTree(dataset, color_weight_dict, x_const)
    t_end = time.time_ns()
    
    build_times.append((t_end - t_start) / (10 ** 9))
    print(f"Build time: {(t_end - t_start) / (10 ** 9)} seconds") 
    
    # query tree
    num_valid_samples = 0
    color_samples = list()
    t_sum = 0
    for i in range(num_iterations):
        x_range = [round(random.random(),3), round(random.random(),3)]  
        y_range = [round(random.random(),3), round(random.random(),3)]
        
        if x_range[0] > x_range[1]:
            (x_range[0], x_range[1]) = (x_range[1], x_range[0])
        if y_range[0] > y_range[1]:
            (y_range[0], y_range[1]) = (y_range[1], y_range[0])
    
        t_start = time.time_ns()
        
        rand_color_sample = tree.report_colors(x_range, y_range)
        if rand_color_sample is not None:
            color_samples.append(rand_color_sample)
            num_valid_samples += 1
            
        t_end = time.time_ns()
        t_sum += t_end - t_start
    t_avg = t_sum / num_iterations
        
    query_times.append((t_avg) / (10 ** 6))
    print(f"Query time: {(t_avg) / (10 ** 6)} miliseconds")
    print(f"  Average of {num_iterations} samples ({round(num_valid_samples/num_iterations, 3)} % valid)")
    
    light_percents.append(tree.light_count / (tree.light_count + tree.heavy_count) * 100)
    print(f"Light %: {round(tree.light_count / (tree.light_count + tree.heavy_count), 3) * 100}\n")

    # color_counts = [0] * num_colors
    # for it, color in enumerate(color_samples):
    #     idx = color - 1
    #     color_counts[idx] += 1
    
    # color_freqs = [0] * num_colors
    # for it, count in enumerate(color_counts):
    #     if num_valid_samples == 0:
    #         color_freqs[it] = 0
    #     else:
    #         color_freqs[it] = count / num_valid_samples
    
    # if first_iteration:
    #     plt.bar(range(1, num_colors + 1), color_weight_list, color='blue')
    #     plt.title('Weights of colors')
    #     plt.xlabel('Color')
    #     plt.ylabel('Weight')
    #     plt.show()
    #     first_iteration = False
    
    # plt.bar(range(1, num_colors + 1), color_freqs, color='orange')
    # plt.title(f"# {it} - Frequencies of colors from random query sampling")
    # plt.xlabel('Color')
    # plt.ylabel('Frequency')
    # plt.show()

if len(xs) != 1:
    plt.scatter(xs, query_times, color='green')
    plt.title('Query time in relation to X constant')
    plt.xlabel('X Constant (% of n)')
    plt.ylabel('Avg Query time (ms)')
    x = np.array(xs)
    y = np.array(query_times)
    a, b = np.polyfit(x, y, 1)
    plt.plot(x, a*x+b) 
    plt.show()
    
    # plt.scatter(xs, build_times, color='red')
    # plt.title('Build time in relation to X constant')
    # plt.xlabel('X Constant (% of n)')
    # plt.ylabel('Build time (s)')
    # x = np.array(xs)
    # y = np.array(build_times)
    # a, b = np.polyfit(x, y, 1)
    # plt.plot(x, a*x+b) 
    # plt.show()
    
    plt.scatter(xs, light_percents, color='red')
    plt.title('Light % in relation to X constant')
    plt.xlabel('X Constant (% of n)')
    plt.ylabel('% of light nodes')
    x = np.array(xs)
    y = np.array(light_percents)
    a, b = np.polyfit(x, y, 1)
    plt.plot(x, a*x+b) 
    plt.show()


# -----------------------------------------------------------------------------

# def find_subset(root):
#     color_set = list()
    
#     if root.left is None and root.right is None:
#         return [root]
    
#     if root.left is not None and root.right is not None:
#         sub_left = find_subset(root.left)
#         sub_right = find_subset(root.right)
        
#         if sub_left:
#             color_set += sub_left
#         if sub_right:
#             color_set += sub_right
    
#     return color_set

# def sort_dataset(dataset, low, high, dim):
#     if low < high:
#         pi = partition(dataset, low, high, dim)
#         sort_dataset(dataset, low, pi, dim)
#         sort_dataset(dataset, pi + 1, high, dim)

# def partition(dataset, low, high, dim):
#     pivot = dataset[(low + high) // 2][dim]
#     i = low - 1
#     j = high + 1
#     while True:
#         while True:
#             i = i + 1
#             if dataset[i][dim] >= pivot:
#                 break
#         while True:
#             j = j - 1
#             if dataset[j][dim] <= pivot:
#                 break
#         if i < j:
#             (dataset[i], dataset[j]) = (dataset[j], dataset[i])
#         else:
#             return j

# def is_in_range(x_range, y_range, coords):
#     in_x = False
#     in_y = False
    
#     if x_range[0] < coords[0] and coords[0] < x_range[1]:
#         in_x = True
        
#     if y_range[0] < coords[1] and coords[1] < y_range[1]:
#         in_y = True 
    
#     return in_x and in_y


# x_range = [0.001, 0.999]
# y_range = [0.001, 0.999]
# (canonical_left, canonical_right) = tree.report_aux_colors(x_range, y_range)

# left_set = list()
# for c in canonical_left:
#     left_set += find_subset(c)
    
# right_set = list()
# for c in canonical_right:
#     right_set += find_subset(c)

# left_colors = list()
# left_points = list()
# left_points_orig = list()
# for point in left_set:
#     left_colors.append(point.color)
#     left_points.append(point.coords)    
#     left_points_orig.append(point.orig_coords)

# right_colors = list()
# right_points = list()
# right_points_orig = list()
# for point in right_set:
#     right_colors.append(point.color)
#     right_points.append(point.coords)
#     right_points_orig.append(point.orig_coords)

# # sort_dataset(left_points, 0, len(left_points) - 1, 1)
# # sort_dataset(right_points, 0, len(left_points) - 1, 1)
# # left_points.reverse()
# # right_points.reverse()

# left_colors.sort()
# right_colors.sort()

# # print(f"left colors : {left_colors}")
# # print(f"right colors: {right_colors}")

# print(f"x_range: {x_range}")
# print(f"y_range: {y_range}")

# if len(left_colors) <= num_colors and len(right_colors) <= num_colors:
#     print("\nNo duplicate colors")
# else:
#     print("\nDuplicate colors")
#     # print(f"left points : {left_points}")
#     # print(f"right points: {right_points}")
#     # print(f"left orig : {left_points_orig}")
#     # print(f"right orig: {right_points_orig}")

# all_set = left_set + right_set
# all_in_range = True
# error_points = list()
# error_points_orig = list()

# for point in all_set:
#     if not is_in_range(x_range, y_range, point.orig_coords):
#         all_in_range = False
#         error_points.append(point.coords)
#         error_points_orig.append(point.orig_coords)
        
# if all_in_range:
#     print("\nAll in range")
# else:
#     print("\nNot all in range")
#     print(error_points)
#     print(error_points_orig)