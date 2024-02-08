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

# name selected 6 numerical columns (dimensions)
columnsUsedNum = ['age', 'fnlwgt', 'education-num', 'capital-gain', 'capital-loss', 'hours-per-week']
# name selected 2 categorical columns (colors) 
columnsUsedColor = ['race', 'sex']
# read csv file, comma seperated, no header in csv file, set names of columns, set used columns
dataNum = pd.read_csv('adult.data', sep=',', header=None, names=columnNames, usecols=columnsUsedNum)
dataColor = pd.read_csv('adult.data', sep=',', header=None, names=columnNames, usecols=columnsUsedColor)
# generate dataframe using data
dataframeNum = pd.DataFrame(dataNum)
dataframeColor = pd.DataFrame(dataColor)

datasetNum = dataframeNum.to_numpy().tolist()
datasetColor = dataframeColor.to_numpy().tolist()

races = [' White', ' Asian-Pac-Islander', ' Amer-Indian-Eskimo', ' Other', ' Black']
sexes = [' Male', ' Female']

num_dim = len(datasetNum[0]) 

# normalize numerical data:
    
# 1. find min and max for every dimension (column)
min = list(range(num_dim))
max = list(range(num_dim))

for column in range(num_dim):
    min[column] = np.inf
    max[column] = -np.inf
    for row in range(len(datasetNum)):        
        if datasetNum[row][column] < min[column]:
            min[column] = datasetNum[row][column]
            
        if datasetNum[row][column] > max[column]:
            max[column] = datasetNum[row][column]

# 2. apply normalization
for column in range(num_dim):
    for row in range(len(datasetNum)):        
        datasetNum[row][column] = (datasetNum[row][column] - min[column]) / (max[column] - min[column])

# print distributions of data in each column
for column in range(num_dim):
    bucket_size = 100
    buckets = [0] * bucket_size
    for row in range(len(datasetNum)):        
        num = math.trunc(datasetNum[row][column] * bucket_size)
        buckets[num - 1] += 1

    # plt.bar(range(1, len(buckets) + 1), buckets, color='red')
    # plt.title(f'Distribution of column {columnsUsedNum[column]}')
    # plt.xlabel('Bucket')
    # plt.ylabel('Count')
    # plt.show()

# assign each color to an integer value
color_int_dict = dict()
i = 1
for race in races:
    for sex in sexes:
        color_int_dict[race + "/" + sex] = i
        i = i + 1

num_colors = len(color_int_dict)
print(f"Input size: {len(datasetNum)}")
print(f"Number of dimensions: {num_dim}")
print(f"Number of colors: {num_colors}\n")  

dataset = [None] * len(datasetNum)
# take out race and sex from each data point and assign the two as the color of the point
for i in range(len(dataset)):
    race = datasetColor[i][0]
    sex = datasetColor[i][1]
    colored_point = (color_int_dict[race + "/" + sex], datasetNum[i])
    dataset[i] = colored_point

color_freq_list = list()
for i in range(num_colors):
    color_freq_list.append(0)

for color, coord in dataset:
    color_freq_list[int(color) - 1] = color_freq_list[int(color) - 1] + 1 

color_weight_dict = dict()
color_weight_list = list()
for i in range(1, len(color_int_dict) + 1):
    color_weight_dict[str(i)] = 1 / (color_freq_list[i - 1] / len(dataset) ** 2)
    color_weight_list.append(1 / (color_freq_list[i - 1] / len(dataset)) ** 2) 
    # color_weight_dict[str(i)] = 1
    # color_weight_list.append(1) 

# initialize counts of colors to 0
color_counts = list()
for i in range(num_colors):
    color_counts.append(0)

num_build_iterations = 1
for i in range(1, num_build_iterations + 1):
    # print(f'Build trial #{i}:')
    t = time.time_ns()
    tree = KDTree.KDTree(dataset, color_weight_dict)
    print('Build time:', ((time.time_ns() - t) / (10 ** 9)), 'seconds')
    
    min = [None] * num_dim
    max = [None] * num_dim
    
    for column in range(num_dim):
        min[column] = np.inf
        max[column] = -np.inf
        for row in range(len(dataset)):
            if dataset[row][1][column] < min[column]:
                min[column] = dataset[row][1][column]
                
            if dataset[row][1][column] > max[column]:
                max[column] = dataset[row][1][column]
                
    
    num_query_iterations = 1000
    t_sum = 0
    none_count = 0
    for i in range(num_query_iterations):
        min_coords = [None] * num_dim
        max_coords = [None] * num_dim
        
        for column in range(num_dim):
            min_coords[column] = 0.9 * np.random.random()
            max_coords[column] = min_coords[column] + 0.1
                
            if min_coords[column] > max_coords[column]:
                (min_coords[column], max_coords[column]) = (max_coords[column], min_coords[column])
        
        min_coords[3] = 0
        max_coords[3] = 1
        min_coords[4] = 0
        max_coords[4] = 1
        min_coords[5] = 0
        max_coords[5] = 1
        
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
    
    print(f"Avg query time ({num_query_iterations} trials): {(t_sum / (10 ** 6)) / num_query_iterations} miliseconds")
    success_rate = (num_query_iterations - none_count) / num_query_iterations
    print('Success rate:', success_rate, '\n')

# find frequencies of colors
color_freqs = [None] * num_colors
for i in range(num_colors):
    color_freqs[i] = color_counts[i] / (num_query_iterations * num_build_iterations * success_rate)

sum = 0
for count in tree.color_counts:
    sum += count
    
for i in range(len(tree.color_counts)):
    tree.color_counts[i] /= sum


tree.color_counts.append(0)
tree.color_counts.append(1)
plt.bar(range(1, len(tree.color_counts) + 1), tree.color_counts, color='green')
plt.title('Frequencies of colors in range')
plt.xlabel('Color')
plt.ylabel('Frequencies')
plt.show()

plt.bar(range(1, num_colors + 1), color_weight_list, color='blue')
plt.title('Weights of colors')
plt.xlabel('Color')
plt.ylabel('Weight')
plt.show()

color_freqs.append(0)
color_freqs.append(1)
plt.bar(range(1, len(color_freqs) + 1), color_freqs, color='orange')
plt.title('Frequencies of colors from random query sampling')
plt.xlabel('Color')
plt.ylabel('Frequency')
plt.show()