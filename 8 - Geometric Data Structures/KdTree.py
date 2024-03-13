# -*- coding: utf-8 -*-
"""
Created on: March 12, 2023
Authors: Nathaniel Madrigal, Alexander Madrigal

Objective:
 - Implement a multidimensional Kd-Tree data structure which can perform 
   independently range sampling on a set of colored (categorical) points
"""
import numpy as np

class KdTree():
    def __init__(self, dataset, color_weights):
        self.num_dim = len(dataset[0]) - 1     # number of dimensions in points
        self.num_colors = len(color_weights)   # number of colors in points
        self.color_weights = color_weights     # dictionary of colors mapped to weights
        self.root = self.build_kdtree(dataset) # root of kdtree
        
    class Node():
        def __init__(self, colored_point):
            self.point = colored_point.copy()
            self.color = self.point.pop()
        
        left = None      # left child
        right = None     # right child
        min_point = None # min point of bounding box 
        max_point = None # max point of bounding box
        weight = None    # weight of subtree rooted at self  
        count = None     # number of leaves in subtree rooted at self
        
    def build_kdtree(self, dataset, depth=0, min_point = None, max_point = None):
        if not dataset:
            return None
        
        # at root, set range of entire dataset
        if min_point is None and max_point is None:
            min_point = list(range(self.num_dim))
            max_point = list(range(self.num_dim))
            # find min and max for every dimension
            for axis in range(self.num_dim):
                min_point[axis] = np.inf
                max_point[axis] = -np.inf
                # search through every point in dataset
                for i in range(len(dataset)):
                    if dataset[i][axis] <= min_point[axis]:
                        min_point[axis] = dataset[i][axis]
                        
                    if dataset[i][axis] >= max_point[axis]:
                        max_point[axis] = dataset[i][axis]
        
        # create leaf
        if len(dataset) == 1: 
            v = self.Node(dataset[0])
            v.min_point = min_point
            v.max_point = max_point
            v.weight = self.color_weights[v.color]
            v.count = 1
        # create internal node
        else:
            axis = depth % self.num_dim
            
            # find median point
            dataset.sort(key=lambda p: p[axis])
            median = len(dataset) // 2
            if len(dataset) % 2 == 0:
                median -= 1
                
            # split dataset by median point and create internal node on median
            v = self.Node(dataset[median])
            v.min_point = min_point
            v.max_point = max_point
            
            dataset_left = dataset[:median + 1]
            dataset_right = dataset[median + 1:]
            min_left = v.min_point
            max_left = v.point
            min_right = v.point
            max_right = v.max_point
            
            v.left = self.build_kdtree(dataset_left, depth + 1, min_left, max_left)
            v.right = self.build_kdtree(dataset_right, depth + 1, min_right, max_right)
            v.weight = v.left.weight + v.right.weight
            v.count = v.left.count + v.right.count
            
        return v

    def query_random_sample(self, min_point, max_point):
        canonical_nodes = self.report_canonical_nodes(self.root, min_point, max_point)
        if not canonical_nodes:
            return None
        
        # randomly select a canonical node
        max_node = canonical_nodes[0]
        max_key = np.random.random() ** (1 / max_node.weight)
        for node in canonical_nodes:
            key = np.random.random() ** (1 / node.weight)
            if key > max_key:
                max_node = node
                max_key = key
                
        # randomly walk down canonical node and return leaf node
        v = max_node
        while v.left is not None and v.right is not None:
            if np.random.random() ** (1 / v.left.weight) > np.random.random() ** (1 / v.right.weight):
                v = v.left
            else:
                v = v.right
        
        return v
                
        
    def report_canonical_nodes(self, root, min_point, max_point, canonical_nodes=[]):
        # search leaf node
        if root.left is None and root.right is None:
            if all(min_point[i] <= root.point[i] <= max_point[i] for i in range(self.num_dim)):
                canonical_nodes.append(root)
        # search internal node
        else:
            # no intersect
            if any(root.min_point[i] > max_point[i] or root.max_point[i] < min_point[i] for i in range(self.num_dim)):
                return canonical_nodes
            # fully intersects
            elif all(min_point[i] <= root.min_point[i] and root.max_point[i] <= max_point[i] for i in range(self.num_dim)):
                canonical_nodes.append(root)
            # partial intersect
            else:
                self.report_canonical_nodes(root.left, min_point, max_point, canonical_nodes)
                self.report_canonical_nodes(root.right, min_point, max_point, canonical_nodes)
            
        return canonical_nodes