# -*- coding: utf-8 -*-
"""
Created on: November 29, 2023
Authors: Nathaniel Madrigal, Alexander Madrigal
"""

import numpy as np

class RangeTree():
    # dataset is a list of colored points
    # colored points have their color as last element of list
    def __init__(self, dataset, color_weight_dict):
        self.num_dim = len(dataset[0]) - 1
        self.color_weight_dict = color_weight_dict.copy()
        self.num_color = len(color_weight_dict)
        self.root = self.build_range_tree(self.build_transformed_dataset(dataset))
        
        # self.root = self.build_range_tree(dataset)
        
    class Node():
        def __init__(self, x_min, y_min, y_max, color):
            # colored_coord is a point with color as last element
            self.x_min = x_min
            self.y_min = y_min
            self.y_max = y_max
            self.color = color          
            
        left = None
        right = None
        weight = None 
        assoc_tree = None
        
    def build_transformed_dataset(self, dataset):
        color_list_dict = dict()
        for i in range(len(dataset)):
            color = dataset[i][-1]
            # if color is in color dictionary, append point
            if color in color_list_dict.keys():
                color_list_dict[color].append(dataset[i])
            # else, create a list with point
            else:
                color_list_dict[color] = [dataset[i]]
        
        transformed_dataset = list()
        for color in color_list_dict:
            color_list = color_list_dict[color].copy()
            if color_list is None:
                continue
            self.sort_dataset(color_list, 0, len(color_list) - 1, 0)
            v = self.Node(color_list[0][0], color_list[0][1], np.inf, color_list[0][2])
            transformed_dataset.append(v)
            
            y_min = color_list[0][1]
            for i in range(1, len(color_list)):
                if color_list[i][1] < y_min:
                    v = self.Node(color_list[i][0], color_list[i][1], y_min, color_list[i][2])
                    transformed_dataset.append(v)
                    y_min = color_list[i][1]
        
        return transformed_dataset
    
    # Returns root of a built d-dimensional range tree
    # dataset: list of colored points
    # dim: current dimension of range tree
    def build_range_tree(self, dataset, dim = None):
        if dim is None:
            dim = 0
        
        if dim >= self.num_dim:
            return None
        
        # build an associated tree with the same set of nodes in the d+1 dimension
        assoc_tree = None
        # self.build_range_tree(dataset, dim + 1)
        
        # base case, create node if dataset contains one point 
        if len(dataset) == 1:
            v = self.Node(dataset[0].x_min, dataset[0].y_min, dataset[0].y_max, dataset[0].color) 
            v.count = 1
            v.weight = self.color_weight_dict[v.color]
        # recursive case, dataset has more than one point
        else:
            # sort the dataset and split into two sublists by median point
            self.sort_dataset(dataset, 0, len(dataset) - 1, dim)
            
            if len(dataset) % 2 == 0:
                mid = (len(dataset) // 2) - 1
            else:
                mid = len(dataset) // 2
            dataset_left = dataset[:mid + 1]
            dataset_right = dataset[mid + 1:]
            
            # create a node v from median point
            v = self.Node(dataset[mid].x_min, dataset[mid].y_min, dataset[mid].y_max, dataset[mid].color)
            v.left = self.build_range_tree(dataset_left, dim)
            v.right = self.build_range_tree(dataset_right, dim)
            v.count = v.left.count + v.right.count
            v.weight = v.left.weight + v.right.weight
            
        v.assoc_tree = assoc_tree
        return v
    
    # sort dataset at certain dimension using quicksort
    def sort_dataset(self, dataset, low, high, dim):
        if low < high:
            # pidx: partition index
            pidx = self.partition(dataset, low, high, dim)
            self.sort_dataset(dataset, low, pidx, dim)
            self.sort_dataset(dataset, pidx + 1, high, dim)
    
    # helper function for sort_dataset function
    def partition(self, dataset, low, high, dim):
        pivot = dataset[(low + high) // 2]
        i = low - 1
        j = high + 1
        while True:
            while True:
                i = i + 1
                if isinstance(dataset[i], self.Node):
                    if dataset[i].x_min >= pivot.x_min:
                        break
                else:
                    if dataset[i][dim] >= pivot[dim]:
                        break
            while True:
                j = j - 1
                if isinstance(dataset[i], self.Node):
                    if dataset[j].x_min <= pivot.x_min:
                        break
                else:
                    if dataset[j][dim] <= pivot[dim]:
                        break
            if i < j:
                (dataset[i], dataset[j]) = (dataset[j], dataset[i])
            else:
                return j
            
    # returns number of unique colors which intersect orthant
    # orthant: a point of type {ai,...,ad} which implicitly defines the region [-inf, ai] x ... x [-inf, ad]
    def query_range_tree(self, orthant):
        canonical_nodes = self.find_canonical_nodes(self.root, orthant)
        
        # return if no canonical nodes found
        if not canonical_nodes:
            return None
        
        # find list of nodes bounded by y
        sub_nodes = list()
        for c in canonical_nodes:
            L = self.report_subtree(self.root)
            if L:
                sub_nodes += L
        
        sub_nodes_inty = list()
        for i, sn in enumerate(sub_nodes):
            if orthant[1] < sn.y_min or orthant[1] >= sn.y_max:
                sub_nodes_inty.append(sub_nodes[i])
        
        # c_max: node with greatest key
        # initialize c_max as the first index of C
        c_max = sub_nodes_inty[0]
        c_max_key = np.random.random() ** (1 / c_max.weight)
        
        # loop from second node to end of C
        # find the canonical node with the greatest key in C and assign to c_max
        for i in range(1, len(sub_nodes_inty)):
            c = sub_nodes_inty[i]
            c_key = np.random.random() ** (1 / c.weight)
            # replace c_max if the current canonical node has a greater key
            if c_key > c_max_key:
                c_max = c
                c_max_key = c_key
        return c_max
        
        
    def report_subtree(self, root):
        L = list()
        if root is None:
            return L
        if root.left is None and root.right is None:
            L.append(root)
            return L 
        else:
            L_left = self.report_subtree(root.left)
            L_right = self.report_subtree(root.right)
            if L_left:
                L += L_left
            if L_right:
                L += L_right
            return L
    
    def find_canonical_nodes(self, root, orthant):
        canonical_nodes = list()
        # if v is leaf, check if in range
        v = root
        if v.left is None and v.right is None:
            if v.x_min <= orthant[0]:
                canonical_nodes.append(v)
                
        # v is internal node, follow path to x boundary 
        else:       
            # traverse down tree until leaf node
            while v.left is not None and v.right is not None:
                if v.x_min <= orthant[0]:
                    canonical_nodes.append(v.left)
                    v = v.right
                else:
                    v = v.left
            # check leaf node for intersection
            if v.x_min <= orthant[0]:
                canonical_nodes.append(v) 
        return canonical_nodes