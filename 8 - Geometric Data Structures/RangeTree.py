# -*- coding: utf-8 -*-
"""
Created on: March 12, 2023
Authors: Nathaniel Madrigal, Alexander Madrigal

Objective:
 - Implement a multidimensional Range Tree data structure which can perform 
   independently range sampling on a set of colored (categorical) points
 - With fractional cascading on the lowest level of Range Tree
"""
import numpy as np
import time

class RangeTree():
    def __init__(self, dataset, color_weights):
        self.num_dim = len(dataset[0]) - 1     # number of dimensions in points
        self.num_colors = len(color_weights)   # number of colors in points
        self.color_weights = color_weights     # dictionary of colors mapped to weights
        self.root = self.build_range_tree(dataset) # root of kdtree
        
    class Node():
        def __init__(self, colored_point):
            self.point = colored_point.copy()
            self.color = self.point.pop()
        
        left = None    # left child
        right = None   # right child
        T_assoc = None # next level range tree
        weight = None  # weight of subtree rooted at self  
        count = None   # number of leaves in subtree rooted at self
        
    def build_range_tree(self, dataset, axis=0):
        if not dataset:
            return None
        
        if axis > (self.num_dim - 1):
            return None
        
        # create associated tree on higher axis
        T_assoc = self.build_range_tree(dataset, axis + 1)
        
        # create leaf
        if len(dataset) == 1: 
            v = self.Node(dataset[0])
            v.T_assoc = T_assoc
            v.weight = self.color_weights[v.color]
            v.count = 1
        # create internal node
        else:
            # find median point
            dataset.sort(key=lambda p: p[axis])
            median = len(dataset) // 2
            if len(dataset) % 2 == 0:
                median -= 1
            
            # split dataset by median point and create internal node on median
            dataset_left = dataset[:median + 1]
            dataset_right = dataset[median + 1:]
            
            v = self.Node(dataset[median])
            v.left = self.build_range_tree(dataset_left, axis)
            v.right = self.build_range_tree(dataset_right, axis)
            v.T_assoc = T_assoc
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
        
    def report_canonical_nodes(self, root, min_point, max_point, axis=0, canonical_nodes=[]):
        sp = self.report_split_node(self.root, min_point, max_point, axis)
        
        # search leaf node
        if sp.left is None and sp.right is None:
            if min_point[axis] <= root.point[axis] <= max_point[axis]:
                canonical_nodes.append(sp)
        # search internal node
        else:
            # follow path to min_point
            v = sp.left
            while v.left is not None and v.right is not None:
                if v.point[axis] >= min_point[axis]:
                    # recursively find canonical nodes on higher axis if not at highest axis
                    # otherwise add v to canonical nodes
                    if axis < self.num_dim - 1:
                        self.report_canonical_nodes(v.right, min_point, max_point, axis + 1, canonical_nodes)
                    else:
                        canonical_nodes.append(v.right)
                    v = v.left
                else:
                    v = v.right
            # check leaf at end of path
            if min_point[axis] <= v.point[axis] <= max_point[axis]:
                canonical_nodes.append(v)
                
            # repeat process on path to max_point
            v = sp.right
            while v.left is not None and v.right is not None:
                if v.point[axis] <= max_point[axis]:
                    if axis < self.num_dim - 1:
                        self.report_canonical_nodes(v.left, min_point, max_point, axis + 1, canonical_nodes)    
                    else:
                        canonical_nodes.append(v.left)
                    v = v.right
                else:
                    v = v.left
            if min_point[axis] <= v.point[axis] <= max_point[axis]:
                canonical_nodes.append(v)
                
        return canonical_nodes

    def report_split_node(self, root, min_point, max_point, axis): 
        v = root
        # walk down v until leaf or inside axis range
        while v.left is not None and v.right is not None:
            if v.point[axis] < min_point[axis]:
                v = v.right
            elif v.point[axis] > max_point[axis]:
                v = v.left
            else:
                break
        return v