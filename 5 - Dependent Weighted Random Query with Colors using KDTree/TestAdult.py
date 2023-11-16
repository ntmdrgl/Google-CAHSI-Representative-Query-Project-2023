# -*- coding: utf-8 -*-
"""
Created on: November 16, 2023
Authors: Alexander Madrigal, Nathaniel Madrigal
"""

import KDTree
import numpy as np
import pandas as pd
import math
import time
from matplotlib import pyplot as plt

# name all 15 columns of data
columnNames = ['age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 'occupation', 'relationship', 'race', 'sex', 'capital-gain', 'capital-loss', 'hours-per-week', 'native-country', 'income']
# name all 8 columns needed
columnsUsed = ['age', 'fnlwgt', 'education-num', 'race', 'sex', 'capital-gain', 'capital-loss', 'hours-per-week']
# read csv file, comma seperated, no header in csv file, set names of columns, set used columns
data = pd.read_csv('adult.data', sep=',', header=None, names=columnNames, usecols=columnsUsed)
# generate dataframe using data
dataframe = pd.DataFrame(data)
# print(dataframe) # uncomment to glimse at entire dataset

#generate dataset (list of lists) from dataframe
dataset = dataframe.to_numpy().tolist()
# dimensions at indexes 0, 1, 2, 5, 6, 7 (total 6)
# colors at indexes 3, 4  (total unique combinations 10)

races = [' White', ' Asian-Pac-Islander', ' Amer-Indian-Eskimo', ' Other', ' Black']
sexes = [' Male', ' Female']

# assign each color to an integer value
color_int_dict = dict()
i = 1
for race in races:
    for sex in sexes:
        color_int_dict[race + "/" + sex] = i
        i = i + 1

# take out race and sex from each data point and assign the two as the color of the point
for i, point in enumerate(dataset):
    race = point.pop(3)
    sex = point.pop(3)
    colored_point = (color_int_dict[race + "/" + sex], point)
    dataset[i] = colored_point

num_colors = len(color_int_dict)
num_dim = len(dataset[0][1])

color_freq_list = list()
for i in range(num_colors):
    color_freq_list.append(0)

for color, coord in dataset:
    color_freq_list[int(color) - 1] = color_freq_list[int(color) - 1] + 1 

color_weight_dict = dict()
color_weight_list = list()
for i in range(1, len(color_int_dict) + 1):
    # color_weight_dict[str(i)] = 1000 * (0.5 * math.exp(-0.5 * i))
    color_weight_dict[str(i)] = 1 / (color_freq_list[i - 1] / len(dataset))
    color_weight_list.append(1 / (color_freq_list[i - 1] / len(dataset)))
    
print(f"Input size: {len(dataset)}")
print(f"Number of dimensions: {len(dataset[0][1])}\n")    

t = time.time_ns()
tree = KDTree.KDTree(dataset, color_weight_dict)
print('Build time:', ((time.time_ns() - t) / (10 ** 6)), 'ms')

# initialize counts of colors to 0
color_counts = list()
for i in range(num_colors):
    color_counts.append(0)

# rng = np.random.default_rng()

min = list(range(num_dim))
max = list(range(num_dim))

for column in range(num_dim):
    min[column] = np.inf
    max[column] = -np.inf
    for row in range(len(dataset)):
        if dataset[row][1][column] < min[column]:
            min[column] = dataset[row][1][column]
            
        if dataset[row][1][column] > max[column]:
            max[column] = dataset[row][1][column]
            

num_iterations = 200
t_sum = 0
none_count = 0
for i in range(num_iterations):
    # create query range
    min_coords = list(range(num_dim))
    max_coords = list(range(num_dim))
    for column in range(num_dim):
        min_coords[column] = int((0.0001 * (max[column] - min[column])) * np.random.random() + min[column])
        max_coords[column] = int(min_coords[column] + (0.9999 * (max[column] - min[column]) * np.random.random()))
        
        if min_coords[column] > max_coords[column]:
            (min_coords[column], max_coords[column]) = (max_coords[column], min_coords[column])
    
    # query random node over multiple trials
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
        
    

