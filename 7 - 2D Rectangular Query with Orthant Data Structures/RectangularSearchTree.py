# -*- coding: utf-8 -*-
"""
Created on February 7, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal

"""

import OrthogonalSearchTree as OSTree
import MaxEmptyOrthTree as MEOTree
import numpy as np
import time
import math

class RectangularSearchTree():
    def __init__(self, dataset, color_weights, x_const):
        self.num_dim = 2
        self.num_colors = len(color_weights)
        self.size = len(dataset)
        self.color_weights = color_weights.copy()
        self.x_const = x_const
        
        self.root = self.build_tree(dataset)
        
        self.light_count = 0
        self.heavy_count = 0
        
        
    class Node():
        def __init__(self, point):
            self.coords = point.copy()
            self.color = self.coords.pop()
            
        left = None
        right = None
        weight = None
        search_weight = None
        count = None
        
        aux_left = None
        aux_right = None
        
        matrix = None
        left_to_idx = None
        right_to_idx = None
        
    class BoundingBox():
        def __init__(self, min_coords, max_coords):
            self.min_coords = min_coords.copy()
            self.max_coords = max_coords.copy()
            
    # tranform a list of 2d points into colored disjoint boxes (represented by _d points)
    def transform_dataset(self, dataset, isTypeLeft):
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
            meo_tree = MEOTree.MaxEmptyOrthTree(color_list, self.color_weights)
            
            # query to find 'skyline' points
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
            # print(f"Query MEO time: {(t_end - t_start) / (10 ** 9)} seconds")
            
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
                        
                        # overhang has z min boundary
                        # transformed_dataset.append([-np.inf, p[0], p[1], np.inf, prev[2], p[2], True, p[-1]])
                        # # under has updated z max boundary
                        # transformed_dataset.append([-np.inf, p[0], p[1], prev[1], -np.inf, prev[2], True, p[-1]])
                else:
                    # create y max bound if under previous point (from z)
                    if p[2] > sky_list[it - 1][2]:
                        # make y max the prev y
                        transformed_dataset.append([-np.inf, p[0], p[1], prev[1], p[2], np.inf, False, p[-1]])
                    # make two boxes, 1. one with overhang 2. other under prev point (from z) 
                    else:
                        # overhang is incomplete
                        transformed_dataset.append([-np.inf, p[0], p[1], prev[1], p[2], np.inf, False, p[-1]])
                        
                        # overhang has z max boundary
                        # transformed_dataset.append([-np.inf, p[0], p[1], np.inf, p[2], prev[2], False, p[-1]])
                        # under has updated z min boundary
                        # transformed_dataset.append([-np.inf, p[0], p[1], prev[1], prev[2], np.inf, False, p[-1]])
            
        return transformed_dataset
        
        
    def build_tree(self, dataset, depth = 0):
        # base case, dataset is at leaf node v
        if len(dataset) == 1:
            v = self.Node(dataset[0])
            v.weight = self.color_weights[v.color]
            v.count = 1
            
        # dataset is at internal node v
        else:
            # split dataset on median node sorted on y dimension
            self.sort_dataset(dataset, 0, len(dataset) - 1, 1)  
                      
            if len(dataset) % 2 == 0:
                mid = (len(dataset) // 2) - 1
            else:
                mid = len(dataset) // 2
                            
            # set v as the median internal node
            v = self.Node(dataset[mid])
            
            # assign left and right pointers to trees built on split subtrees
            dataset_left = dataset[:mid + 1]
            dataset_right = dataset[mid + 1:]
            v.left = self.build_tree(dataset_left, depth + 1)
            v.right = self.build_tree(dataset_right, depth + 1)
                   
            # assign v's weight to the sum of its childrens weights
            v.weight = v.left.weight + v.right.weight
            
            # create the left and right auxilary structures
            transform_left = self.transform_dataset(dataset_left, True)
            transform_right = self.transform_dataset(dataset_right, False)
            v.aux_left = OSTree.OrthogonalSearchTree(transform_left, self.color_weights)
            v.aux_right = OSTree.OrthogonalSearchTree(transform_right, self.color_weights)
            
            # v.count = v.left.count + v.right.count + v.aux_left.root.count + v.aux_right.root.count + 1
            v.matrix = self.build_matrix(v)
                
        return v
        
    def build_matrix(self, node):
        heavy_left = list()
        heavy_right = list()
        
        heavy_left = self.find_heavy_nodes(node.aux_left.root)
        heavy_right = self.find_heavy_nodes(node.aux_right.root)
        
        if not heavy_left or not heavy_right:
            return None
        
        matrix = [ [None] * len(heavy_right) for i in range(len(heavy_left))]
        
        node.left_to_idx = dict()
        node.right_to_idx = dict()
        
        for it, c_left in enumerate(heavy_left):
            node.left_to_idx[c_left.node_id] = it
        for it, c_right in enumerate(heavy_right):
            node.right_to_idx[c_right.node_id] = it
            
        for i, c_left in enumerate(heavy_left):
            for j, c_right in enumerate(heavy_right):
                self.found_intersection = False
                self.find_light_intersection(c_left, c_right)
                
                matrix[i][j] = self.intersection_weight   
        
        return matrix
        
    def find_heavy_nodes(self, root):
        C = list()
        
        if root is None:
            return C
        
        if root.left is None and root.right is None:
            return C
        
        if root.weight > self.x_const:
            C.append(root)
        
        c_left = self.find_heavy_nodes(root.left)
        c_right = self.find_heavy_nodes(root.right)
        
        if c_left:
            C += c_left
        if c_right:
            C += c_right
            
        return C
    
    def report_colors(self, x_range, y_range):
        split_node = self.find_split_node(self.root, y_range)
        
        # check if in y_range when split_node is leaf
        if split_node.left is None and split_node.right is None:
            if split_node.coords[1] >= y_range[0] and split_node.coords[1] < y_range[1]:
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
                self.found_intersection = False
                self.find_intersection(c_left, c_right, split_node)
                
                nodes_right[j].search_weight -= self.intersection_weight
                if nodes_right[j].search_weight < 0:
                    nodes_right[j].search_weight = 0
        
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
    
    # global vars used to stop tree recursive search when intersection found
    #  in find_light_intersection and find_light_intersection_helper
    found_intersection = None
    intersection_weight = None    
    
    def find_intersection(self, c_left, c_right, node):        
        # self.find_light_intersection(c_left, c_right)
        
        if c_left.weight > self.x_const and c_right.weight > self.x_const:
            self.find_heavy_intersection(c_left, c_right, node)
            self.heavy_count += 1
            # print(c_left.weight, '>', self.x_const)
            
        else:
            # print(c_left.weight, '!>', self.x_const)
            self.find_light_intersection(c_left, c_right)
            self.light_count += 1
    
    def find_heavy_intersection(self, c_left, c_right, node):
        left_idx = node.left_to_idx[c_left.node_id]
        right_idx = node.right_to_idx[c_right.node_id]
        
        self.intersection_weight = node.matrix[left_idx][right_idx]
        self.found_intersection = True
        
        # print('Heavy intersect:', self.intersection_weight)
    
    def find_light_intersection(self, c_left, c_right):
        if c_left is None:
            return
        
        # when at leaf, remove leaf's color from subtree at c_right
        if c_left.left is None and c_left.right is None:
            self.found_intersection = False
            self.find_light_intersection_helper(c_left.color, c_right, c_right)
        
        self.find_light_intersection(c_left.left, c_right)
        self.find_light_intersection(c_left.right, c_right)
    
    def find_light_intersection_helper(self, color, c_right, root):
        if root is None or self.found_intersection is True:
            return
        
        # when at leaf, subtract c_right's weight by weight of searched color
        if root.left is None and root.right is None:
            self.intersection_weight = self.color_weights[color]
            self.found_intersection = True
            return
            
        self.find_light_intersection_helper(color, c_right, root.left)
        self.find_light_intersection_helper(color, c_right, root.right)
        
    
    def report_aux_colors(self, x_range, y_range):
        split_node = self.find_split_node(self.root, y_range)
        
        # check if in y_range when split_node is leaf
        if split_node.left is None and split_node.right is None:
            if split_node.coords[1] >= y_range[0] and split_node.coords[1] < y_range[1]:
                return ([split_node.color], [])
            else:
                return None

        min_left = [-np.inf, x_range[0], -np.inf, x_range[1], -np.inf, y_range[0]]
        max_left = [x_range[0], np.inf, x_range[1], np.inf, y_range[0], np.inf]
        nodes_left = split_node.aux_left.report_colors(min_left, max_left)
        
        min_right = [-np.inf, x_range[0], -np.inf, x_range[1], -np.inf, y_range[1]]
        max_right = [x_range[0], np.inf, x_range[1], np.inf, y_range[1], np.inf]
        nodes_right = split_node.aux_right.report_colors(min_right, max_right)  
        
        return (nodes_left, nodes_right)        
    
    def find_split_node(self, root, y_range):
        v = root
        # loop until node v is at a leaf or is inside y_range
        while (v.left is not None and v.right is not None and (v.coords[1] < y_range[0] or v.coords[1] > y_range[1])):
            if v.coords[1] >= y_range[1]:
                v = v.left
            else:
                v = v.right
        return v
    
    # quick sort implementation to sort dataset on d dimension in ascending order
    def sort_dataset(self, dataset, low, high, dim):
        if low < high:
            pi = self.partition(dataset, low, high, dim)
            self.sort_dataset(dataset, low, pi, dim)
            self.sort_dataset(dataset, pi + 1, high, dim)
    
    # helper function of sort_dataset
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