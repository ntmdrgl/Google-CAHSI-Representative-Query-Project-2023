# -*- coding: utf-8 -*-
"""
Created on February 7, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal

"""

import OrthantSearchTree as ost
import numpy as np

class RectangularSearchTree():
    def __init__(self, dataset, color_weights):
        self.num_dim = len(dataset[0]) - 1
        self.num_colors = len(color_weights)
        
        self.color_weights = color_weights.copy()
        self.root = self.build_tree(dataset)
        
    class Node():
        def __init__(self, point):
            self.coords = point.copy()
            self.color = self.coords.pop()
            
        left = None
        right = None
        box = None
        weight = None
        
    class BoundingBox():
        def __init__(self, min_coords, max_coords):
            self.min_coords = min_coords.copy()
            self.max_coords = max_coords.copy()
            
    # tranform a list of 3d points into colored disjoint boxes (represented by 6d points)
    def transform_dataset(self, dataset):
        # create a dict of size num_colors, each element containing a list of one distinct color
        color_buckets = dict()
        for i in range(len(dataset)):
            color = dataset[i][-1]
            # if color is in color dictionary, append point
            if color in color_buckets.keys():
                color_buckets[color].append(dataset[i])
            # else, create a list with point
            else:
                color_buckets[color] = [dataset[i]]
        
        # for each color create a list ordered by the x coordinate of the dataset
        transformed_dataset = list()
        for color in color_buckets:
            color_list = color_buckets[color].copy()
            self.sort_dataset(color_list, 0, len(color_list) - 1, 0)
            
            # create six dimensional points representing colored disjoint boxes
            # transform minimum point
            v = [color_list[0][0], np.inf, color_list[0][1], np.inf, color_list[0][2], np.inf, color_list[0][-1]]
            transformed_dataset.append(v)
            
            # transform rest of list 
            
            
        return transformed_dataset
        
        
    def build_tree(self, dataset):
        self.transform_dataset(dataset)
        
    
    # sort_dataset implementation to sort dataset in dataset
    def sort_dataset(self, dataset, low, high, dim):
        if low < high:
            pi = self.partition(dataset, low, high, dim)
            self.sort_dataset(dataset, low, pi, dim)
            self.sort_dataset(dataset, pi + 1, high, dim)
    
    # helper function to find partition in sort_dataset
    def partition(self, dataset, low, high, dim):
        pivot = dataset[(low + high) // 2][dim]
        i = low - 1
        j = high + 1
        while True:
            while True:
                i = i + 1
                if dataset[i][dim] >= pivot:
                    break
            while True:
                j = j - 1
                if dataset[j][dim] <= pivot:
                    break
            if i < j:
                (dataset[i], dataset[j]) = (dataset[j], dataset[i])
            else:
                return j