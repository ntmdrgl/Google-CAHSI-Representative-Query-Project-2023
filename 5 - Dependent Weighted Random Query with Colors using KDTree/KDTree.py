# -*- coding: utf-8 -*-
"""
Created on: November, 2023
Authors: Nathaniel Madrigal, Alexander Madrigal
"""

import numpy as np

class KDTree():        
    def __init__(self, dataset, color_weight_dict):
        self.max_dimension = len(dataset[0][1])
        self.color_weight_dict = color_weight_dict
        self.root = self.build_kdtree(dataset)        
    
    class Node():
        def __init__(self, colored_coord):
            (self.color, self.coord) = colored_coord
            self.color = str(self.color)
            
        left = None
        right = None
        box = None
        key = None
        maxNode = None # pointer to child with greatest key
        
    class BoundingBox():
        def __init__(self, min_coords, max_coords):
            self.min_coords = min_coords
            self.max_coords = max_coords
        
    # returns the root of KD tree
    # dataset: list of tuples which contains color and list of coordinates
    # depth: depth of tree
    # B: bounding box of root node
    def build_kdtree(self, dataset, depth = None, B = None):
        # at root, set depth to 0
        if depth is None:
            depth = 0
        # at root, set bounding box to range of P
        if B is None:
            min_coords = list(range(self.max_dimension))
            max_coords = list(range(self.max_dimension))
            
            # find max and min for every dimension
            for dim in range(self.max_dimension):
                min_coords[dim] = np.inf
                max_coords[dim] = -np.inf
                # search through every point in dataset
                for i in range(len(dataset)):
                    if dataset[i][1][dim] < min_coords[dim]:
                        min_coords[dim] = dataset[i][1][dim]
                        
                    if dataset[i][1][dim] > max_coords[dim]:
                        max_coords[dim] = dataset[i][1][dim]
                        
            B = self.BoundingBox(min_coords, max_coords)
            
        # base case, dataset has one point
        # create leaf node, v with value of point 
        # set v's box to itself
        # set v's weight to the weight of its color
        if len(dataset) == 1:
            v = self.Node(dataset[0])
            v.box = B
            v.key = np.random.random() ** (1 / self.color_weight_dict[v.color])
            v.maxNode = v
        else:         
            # split dataset on median point on curr_dim
            curr_dim = depth % self.max_dimension
            self.sort_dataset(dataset, 0, len(dataset) - 1, curr_dim)  
            
            if len(dataset) % 2 == 0:
                mid = (len(dataset) // 2) - 1
            else:
                mid = len(dataset) // 2
            dataset_left = dataset[:mid + 1]
            dataset_right = dataset[mid + 1:]
            
            # create an internal node, v with the value of the median point
            # recursively call buildRangeTree on P's left & right sublists to assign v's left & right children 
            v = self.Node(dataset[mid])
            v.box = B
            
            max_coords_left = v.box.max_coords
            max_coords_left[curr_dim] = v.coord[curr_dim]
            min_coords_right = v.box.min_coords
            min_coords_right[curr_dim] = v.coord[curr_dim]
            
            box_left = self.BoundingBox(v.box.min_coords, max_coords_left)
            box_right = self.BoundingBox(min_coords_right, v.box.max_coords)
            
            v.left = self.build_kdtree(dataset_left, depth + 1, box_left)
            v.right = self.build_kdtree(dataset_right, depth + 1, box_right)
            
            # assign v's key to the greatest key between v's left & right
            # assign v's maxNode to the child node with the greater key
            if v.left.key > v.right.key:
                v.key = v.left.key
                v.maxNode = v.left.maxNode
            else:
                v.key = v.right.key
                v.maxNode = v.right.maxNode
                
        return v
    
    # helper function to find partition in sort_dataset
    def partition(self, dataset, low, high, dim):
        pivot = dataset[(low + high) // 2][1][dim]
        i = low - 1
        j = high + 1
        while True:
            while True:
                i = i + 1
                if dataset[i][1][dim] >= pivot:
                    break
            while True:
                j = j - 1
                if dataset[j][1][dim] <= pivot:
                    break
            if i < j:
                (dataset[i], dataset[j]) = (dataset[j], dataset[i])
            else:
                return j
     
    # sort_dataset implementation to sort points in dataset
    def sort_dataset(self, dataset, low, high, dim):
        if low < high:
            pi = self.partition(dataset, low, high, dim)
            self.sort_dataset(dataset, low, pi, dim)
            self.sort_dataset(dataset, pi + 1, high, dim)
        
    

