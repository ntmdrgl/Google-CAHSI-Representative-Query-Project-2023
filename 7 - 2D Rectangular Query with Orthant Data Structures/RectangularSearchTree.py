# -*- coding: utf-8 -*-
"""
Created on March 13, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal

"""

import ThreeSidedSearchtree as TSSTree
import MaxEmptyOrthTree as MEOTree
import numpy as np
import time
import math

class RectangularSearchTree():
    def __init__(self, dataset, color_weights, x_const):
        self.num_dim = len(dataset[0]) - 1   # number of dimensions in points
        self.num_colors = len(color_weights) # number of colors in points
        self.color_weights = color_weights   # dictionary of colors mapped to weights
        self.root = self.build_tree(dataset) # root of kdtree
        
        self.size = None
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
    def build_tree(self, dataset, axis=1):
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
            v.left = self.build_tree(dataset_left, axis)
            v.right = self.build_tree(dataset_right, axis)
            v.weight = v.left.weight + v.right.weight
            v.count = v.left.count + v.right.count
            
            transform_left = self.transform_dataset(dataset_left, True)
            transform_right = self.transform_dataset(dataset_right, False)
            v.aux_left = OSTree.OrthogonalSearchTree(transform_left, self.color_weights)
            v.aux_right = OSTree.OrthogonalSearchTree(transform_right, self.color_weights)
            
        return v
    
    def transform_dataset(self, dataset, isTypeLeft, isPrintable=None):
        # create a dict of size num_colors, each bucket containing a list of one distinct color
        color_buckets = dict()
        for i in range(len(dataset)):           
            color = dataset[i][-1]
            # if color is in color dictionary, append point
            if color in color_buckets.keys():
                color_buckets[color].append(dataset[i])
            # else, create a list with point
            else:
                color_buckets[color] = [dataset[i]]
        
        # for each color, search for maximally empty orthants in every point
        transformed_dataset = list()
        for color in color_buckets:
            color_list = color_buckets[color].copy()
            
            # transform points from (x, y) to (x1, x2, y) by duplicating x 
            for it, point in enumerate(color_list):
                color_list[it] = [point[0], point[0], point[1], point[-1]]
            
            # build MEOTree and find a list of 'skyline' points
            if isPrintable is None:
                meo_tree = MEOTree.MaxEmptyOrthTree(color_list, self.color_weights)
            else:
                t_start = time.time_ns()
                meo_tree = MEOTree.MaxEmptyOrthTree(color_list, self.color_weights)
                t_end = time.time_ns()
                print(f"  MEO build time: {(t_end - t_start) / (10 ** 9)} seconds")
                
            # query to find 'skyline' points
            if isPrintable is None:
                sky_list = list()
                for point in color_list:
                    # change query range depending on left/right type
                    if isTypeLeft:
                        isEmpty = meo_tree.query_is_empty([point[0], -np.inf, point[2]], [np.inf, point[1], np.inf])
                    else:
                        isEmpty = meo_tree.query_is_empty([point[0], -np.inf, -np.inf], [np.inf, point[1], point[2]])
                    
                    if isEmpty:
                        sky_list.append(point)
            else:
                t_start = time.time_ns()
                sky_list = list()
                for point in color_list:
                    # change query range depending on left/right type
                    if isTypeLeft:
                        isEmpty = meo_tree.query_is_empty([point[0], -np.inf, point[2]], [np.inf, point[1], np.inf])
                    else:
                        isEmpty = meo_tree.query_is_empty([point[0], -np.inf, -np.inf], [np.inf, point[1], point[2]])
                    
                    if isEmpty:
                        sky_list.append(point)
                t_end = time.time_ns()
                print(f"  MEO query time: {(t_end - t_start) / (10 ** 9)} seconds")
            
            # transform 3d skyline points into 6d disjoint cubes             
            self.sort_dataset(sky_list, 0, len(sky_list) - 1, 0)
            sky_list.reverse()
            
            for it, p in enumerate(sky_list):
                prev = sky_list[it - 1]
                
                if it == 0:
                    if isTypeLeft:
                        transformed_dataset.append([-np.inf, p[0], p[1], np.inf, -np.inf, p[2], True, p[-1]])
                    else:
                        transformed_dataset.append([-np.inf, p[0], p[1], np.inf, p[2], np.inf, False, p[-1]])
                    continue
            
                if isTypeLeft:
                    # create y max bound if under previous point (from z)
                    if p[2] < sky_list[it - 1][2]:
                        # make y max the prev y
                        transformed_dataset.append([-np.inf, p[0], p[1], prev[1], -np.inf, p[2], True, p[-1]])
                    # make two boxes, 1. one with overhang 2. other under prev point (from z) 
                    else:
                        # overhang is incomplete
                        transformed_dataset.append([-np.inf, p[0], p[1], prev[1], -np.inf, p[2], True, p[-1]])

                else:
                    # create y max bound if under previous point (from z)
                    if p[2] > sky_list[it - 1][2]:
                        # make y max the prev y
                        transformed_dataset.append([-np.inf, p[0], p[1], prev[1], p[2], np.inf, False, p[-1]])
                    # make two boxes, 1. one with overhang 2. other under prev point (from z) 
                    else:
                        # overhang is incomplete
                        transformed_dataset.append([-np.inf, p[0], p[1], prev[1], p[2], np.inf, False, p[-1]])
                
        return transformed_dataset
    
    def query_random_sample(self, min_point, max_point):
        split_node = self.report_split_node(self.root, min_point, max_point)
        
        # check if in y_range when split_node is leaf
        if split_node.left is None and split_node.right is None:
            if min_point[1] <= split_node.point[1] <= max_point[1]:
                return split_node.color
            else:
                return None

        min_left = [-np.inf, x_range[0], -np.inf, x_range[1], -np.inf, y_range[0]]
        max_left = [x_range[0], np.inf, x_range[1], np.inf, y_range[0], np.inf]
        nodes_left = split_node.aux_left.report_colors(min_left, max_left)
        
        min_right = [-np.inf, x_range[0], -np.inf, x_range[1], -np.inf, y_range[1]]
        max_right = [x_range[0], np.inf, x_range[1], np.inf, y_range[1], np.inf]
        nodes_right = split_node.aux_right.report_colors(min_right, max_right)      
        
        
        for c_left in nodes_left:
            c_left.search_weight = c_left.weight
        
        for c_right in nodes_right:
            c_right.search_weight = c_right.weight
        
        # find and remove intersection between every pairing of canonical nodes
        #   present in the left_aux and right_aux structures
        for i, c_left in enumerate(nodes_left):
            for j, c_right in enumerate(nodes_right):
                self.find_intersection(c_left, c_right, split_node)
                
                nodes_right[j].search_weight -= self.intersection_weight
                if nodes_right[j].search_weight < 0:
                    nodes_right[j].search_weight = 0
        
        self.update_canonical_counts(nodes_left, nodes_right)
        
        if nodes_left:
            # all light canonical nodes ready to query from
            c_max = nodes_left[0]
            if c_max.search_weight != 0:
                max_key = np.random.random() ** (1 / c_max.search_weight)
            else:
                max_key = 0
        elif nodes_right:
            c_max = nodes_right[0]
            if c_max.search_weight != 0:
                max_key = np.random.random() ** (1 / c_max.search_weight)
            else:
                max_key = 0
        # no light nodes found
        else:
            return None
        
        # search for canonical node with greatest key between 
        #   the lists nodes_left and nodes_right
        for it, node in enumerate(nodes_left):
            if node.search_weight != 0:
                curr_key = np.random.random() ** (1 / node.search_weight)
            else:
                curr_key = 0
            if curr_key > max_key:
                c_max = node
                max_key = curr_key
        
        for it, node in enumerate(nodes_right):
            if node.search_weight != 0:
                curr_key = np.random.random() ** (1 / node.search_weight)
            else:
                curr_key = 0
            if curr_key > max_key:
                c_max = node
                max_key = curr_key
                
        # traverse down tree and report color from leaf
        v = c_max
        while v.left is not None and v.right is not None:
            if np.random.random() ** (1 / v.left.weight) > np.random.random() ** (1 / v.right.weight):
                v = v.left
            else:
                v = v.right
        
        return v.color
                
        # return v
        
    def report_canonical_nodes(self, root, min_point, max_point, axis=0, canonical_nodes=[]):
        pass
        # sp = self.report_split_node(self.root, min_point, max_point, axis)
        
        # # search leaf node
        # if sp.left is None and sp.right is None:
        #     if min_point[axis] <= root.point[axis] <= max_point[axis]:
        #         canonical_nodes.append(sp)
        # # search internal node
        # else:
        #     # follow path to min_point
        #     v = sp.left
        #     while v.left is not None and v.right is not None:
        #         if v.point[axis] >= min_point[axis]:
        #             # recursively find canonical nodes on higher axis if not at highest axis
        #             # otherwise add v to canonical nodes
        #             if axis < self.num_dim - 1:
        #                 self.report_canonical_nodes(v.right, min_point, max_point, axis + 1, canonical_nodes)
        #             else:
        #                 canonical_nodes.append(v.right)
        #             v = v.left
        #         else:
        #             v = v.right
        #     # check leaf at end of path
        #     if min_point[axis] <= v.point[axis] <= max_point[axis]:
        #         canonical_nodes.append(v)
                
        #     # repeat process on path to max_point
        #     v = sp.right
        #     while v.left is not None and v.right is not None:
        #         if v.point[axis] <= max_point[axis]:
        #             if axis < self.num_dim - 1:
        #                 self.report_canonical_nodes(v.left, min_point, max_point, axis + 1, canonical_nodes)    
        #             else:
        #                 canonical_nodes.append(v.left)
        #             v = v.right
        #         else:
        #             v = v.left
        #     if min_point[axis] <= v.point[axis] <= max_point[axis]:
        #         canonical_nodes.append(v)
                
        # return canonical_nodes

    # split node on x-coordinates (axis=0)
    def report_split_node(self, root, min_point, max_point, axis=0): 
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
    