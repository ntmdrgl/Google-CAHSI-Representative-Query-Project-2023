# -*- coding: utf-8 -*-
"""
Created on March 13, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal

Objective:
 - Create a data structure which performs independent random sampling on colored 
   2D points in polylogarithmic time and near-linear space
 - Main concept is using two opposite 3-sided queries to report all colors
   - Transform 2D points into 3D cubes (-> 6D points)
   - Have to remove intersection of colors between the two queries
     - Light vs Heavy nodes (colors < X or colors >= X)
   - O(n) space and sub-linear time (6D Kd-tree)
"""

import KdTree
import numpy as np
import time
import math

class RSTree():
    def __init__(self, dataset, color_weights, x_const):
        self.num_dim = len(dataset[0]) - 1        # number of dimensions in points
        self.num_colors = len(color_weights)      # number of colors in points
        self.color_weights = color_weights.copy() # dictionary of colors mapped to weights
        self.root = self.build_tree(dataset)      # root of tree
        
        self.size = None
        self.avg_count = None
        self.light_count = 0
        self.heavy_count = 0
        
    class Node():
        def __init__(self, colored_point):
            self.point = colored_point.copy()
            self.color = self.point.pop()
        
        left = None          # left child
        right = None         # right child
        weight = None        # weight of subtree rooted at self  
        search_weight = None # temporary weight of node after intersection removal
        count = None         # number of leaves in subtree rooted at self
        aux_left = None      # 3-sided query tree on type-left points 
        aux_right = None     # 3-sided query tree on type-right points
        
    # tree sorted on y-coordinates (axis=1)
    def build_tree(self, dataset, depth=0):
        axis = 1
        if not dataset:
            return None
        
        # create leaf
        if len(dataset) == 1: 
            v = self.Node(dataset[0])
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
            v.left = self.build_tree(dataset_left, depth + 1)
            v.right = self.build_tree(dataset_right, depth + 1)
            v.weight = v.left.weight + v.right.weight
            v.count = v.left.count + v.right.count
            
            # transform left and right child's dataset
            # and create 3-sided auxillary trees
            transform_left = self.transform_dataset(dataset_left, True)
            transform_right = self.transform_dataset(dataset_right, False)
            v.aux_left = KdTree.KdTree(transform_left, self.color_weights)
            v.aux_right = KdTree.KdTree(transform_right, self.color_weights)
            
        return v
    
    def transform_dataset(self, dataset, isTypeLeft, isPrintable=None):
        # generate lists separated by colors stored in a dictionary
        color_buckets = dict()
        for i in range(len(dataset)):           
            color = dataset[i][-1]
            if not color in color_buckets.keys():
                color_buckets[color] = [dataset[i]]
            else:
                color_buckets[color].append(dataset[i])
            
        # create disjoint cubes for each color and append to transformed dataset 
        transformed_dataset = list()
        
        for color in color_buckets:
            # transform points from (x, y) to (x, y, z) where y is duplicate x
            color_list = color_buckets[color]
            for it, point in enumerate(color_list):
                color_list[it] = [point[0], point[0], point[1], point[-1]]
            
            # find maximally empty points using 3-sided emptiness queries
            emptiness_tree = KdTree.KdTree(color_list, self.color_weights)
            max_empty_points = list()
            for point in color_list:
                if isTypeLeft:
                    min_point = [point[0], -np.inf,  point[2]]
                    max_point = [np.inf,   point[1], np.inf  ]
                else:
                    min_point = [point[0], -np.inf,  -np.inf ]
                    max_point = [np.inf,   point[1], point[2]]
                
                if emptiness_tree.report_emptiness(min_point, max_point):
                    max_empty_points.append(point)
                 
            # if len(max_empty_points) == 0:
            #     print("before",len(color_list))
            
            # transform 3d maximally empty points into 6d disjoint cubes             
            max_empty_points.sort(key=lambda p: p[0])
            for it, p in enumerate(max_empty_points):
                if it == 0:
                    if isTypeLeft:
                        transformed_dataset.append([-np.inf, p[0], p[1], np.inf, -np.inf, p[2], p[-1], p[0], p[2]])
                    else:
                        transformed_dataset.append([-np.inf, p[0], p[1], np.inf, p[2], np.inf, p[-1], p[0], p[2]])
                    continue
                
                prev = max_empty_points[it - 1]
                if isTypeLeft:
                    # create y max bound if under previous point (from z)
                    if p[2] < prev[2]:
                        # make y max the prev y
                        transformed_dataset.append([-np.inf, p[0], p[1], prev[1], -np.inf, p[2], p[-1], p[0], p[2]])
                    else:
                        # overhang case, find all prev points with ...
                        transformed_dataset.append([-np.inf, p[0], p[1], prev[1], -np.inf, p[2], p[-1], p[0], p[2]])

                else:
                    # create y max bound if under previous point (from z)
                    if p[2] > prev[2]:
                        # make y max the prev y
                        transformed_dataset.append([-np.inf, p[0], p[1], prev[1], p[2], np.inf, p[-1], p[0], p[2]])
                    else:
                        # overhang case, find all prev points with ...
                        transformed_dataset.append([-np.inf, p[0], p[1], prev[1], p[2], np.inf, p[-1], p[0], p[2]])
                
                # if it == 0:
                #     if isTypeLeft:
                #         transformed_dataset.append([p[0], np.inf, -np.inf, p[1], p[2], np.inf, p[-1], p[0], p[2]])
                #     else:
                #         transformed_dataset.append([p[0], np.inf, -np.inf, p[1], -np.inf, p[2], p[-1], p[0], p[2]])
                #     continue
                
                # prev = max_empty_points[it - 1]
                # if isTypeLeft:
                #     # point is blocked by previous point on y-axis
                #     if p[2] > prev[2]:
                #         # set y_min to y_max of prev
                #         transformed_dataset.append([p[0], np.inf, prev[1], p[1], p[2], np.inf, p[-1], p[0], p[2]])
                #     # point overhangs prev
                #     else:
                #         # find all prev points with greater x_min in ascending order
                #         # bind y_min by prev y_min and z_max by prev z_min
                #         transformed_dataset.append([p[0], np.inf, prev[1], p[1], p[2], np.inf, p[-1], p[0], p[2]])
                # else:
                #     # point is blocked by previous point on y-axis
                #     if p[2] < prev[2]:
                #         # set y_min to y_max of prev
                #         transformed_dataset.append([p[0], np.inf, prev[1], p[1], -np.inf, p[2], p[-1], p[0], p[2]])
                #     # point overhangs prev
                #     else:
                #         # find all prev points with greater x_min in ascending order
                #         # bind y_min by prev y_min and z_min by prev z_max
                #         transformed_dataset.append([p[0], np.inf, prev[1], p[1], -np.inf, p[2], p[-1], p[0], p[2]])
                
        return transformed_dataset
    
    def query_random_sample(self, min_point, max_point):
        split_node = self.report_split_node(self.root, min_point, max_point)
        # split_node = self.report_split_node(self.root, [x_range[0], y_range[0]], [x_range[1], y_range[1]])
        
        # check if in y_range when split_node is leaf
        if split_node.left is None and split_node.right is None:
            if min_point[1] <= split_node.point[1] <= max_point[1]:
            # if split_node.point[1] >= y_range[0] and split_node.point[1] < y_range[1]:
                return split_node
            else:
                return None
        
        # find canonical nodes from auxillary trees
        min_left = [-np.inf, min_point[0], -np.inf, max_point[0], -np.inf, min_point[1]]
        max_left = [min_point[0], np.inf, max_point[0], np.inf, min_point[1], np.inf]
        canonical_nodes_left = split_node.aux_left.report_colors(min_left, max_left)
        
        min_right = [-np.inf, min_point[0], -np.inf, max_point[0], -np.inf, max_point[1]]
        max_right = [min_point[0], np.inf, max_point[0], np.inf, max_point[1], np.inf]
        canonical_nodes_right = split_node.aux_right.report_colors(min_right, max_right)  
        
        # min_left = [-np.inf, x_range[0], -np.inf, x_range[1], -np.inf, y_range[0]]
        # min_right = [x_range[0], np.inf, x_range[1], np.inf, y_range[0], np.inf]
        # canonical_nodes_left = split_node.aux_left.report_colors(min_left, min_right)
        
        # min_point_right = [-np.inf, x_range[0], -np.inf, x_range[1], -np.inf, y_range[1]]
        # max_point_right = [x_range[0], np.inf, x_range[1], np.inf, y_range[1], np.inf]
        # canonical_nodes_right = split_node.aux_right.report_colors(min_point_right, max_point_right)  
        
        num_counts = 0
        sum_counts = 0
        for node in canonical_nodes_left:
            node.search_weight = node.weight
            num_counts += 1
            sum_counts += node.count
        for node in canonical_nodes_right:
            node.search_weight = node.weight
            num_counts += 1
            sum_counts += node.count
        
        if num_counts != 0:
            self.avg_count = sum_counts / num_counts
        
        # find and remove intersection between every pairing of canonical nodes
        for node_left in canonical_nodes_left:
            for node_right in canonical_nodes_right:
                node_right.search_weight -= self.report_intersection(node_left, node_right)
                if node_right.search_weight < 0:
                    node_right.search_weight = 0
        
        canonical_nodes = list()
        if canonical_nodes_left:
            canonical_nodes += canonical_nodes_left         
        if canonical_nodes_right:
            canonical_nodes += canonical_nodes_left   
        
        if not canonical_nodes:
            return None
        
        # randomly select a canonical node
        max_node = canonical_nodes[0]
        if max_node.weight != 0:
            max_key = np.random.random() ** (1 / max_node.weight)
        else:
            max_key = 0
        for node in canonical_nodes:
            if node.weight != 0:
                key = np.random.random() ** (1 / node.weight)
            else:
                key = 0
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
        
    def report_intersection(self, node_left, node_right):
        # self.heavy_count += 1
        return 0

    # split node on y-coordinates (axis=1)
    def report_split_node(self, root, min_point, max_point):
        axis = 1
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
    