# -*- coding: utf-8 -*-
"""
Created on: November 29, 2023
Authors: Nathaniel Madrigal, Alexander Madrigal

Objective:
- Create a KDTree structure which queries a random point within an orthant range (rectangular region
  that is unbounded on each dimension). Points are queried proportional to the weight of their associated color.
- 
    
Notable Class Functions:
- transform_dataset:
    
- build_kdtree:
    
- query_random_node:
    
- find_canonical_nodes:

"""

import numpy as np

class KDTree():        
    # initialize kdtree class
    # dataset: list of colored points
    #        - points are represented by lists where index is dimension
    #        - color is the last index of each point
    # color_weight_dict: dictionary containing integer colors as keys with positive weights as values
    def __init__(self, dataset, color_weight_dict):
        # set number of dimensions and colors of dataset
        self.dataset_dim = len(dataset[0]) - 1
        self.kdtree_dim = None
        self.num_colors = len(color_weight_dict)
        
        # copy color-weight dictionary and build kdtree
        self.color_weight_dict = color_weight_dict.copy()
        self.root = self.build_kdtree(self.transform_dataset(dataset))
    
    class Node():
        def __init__(self, colored_point):
            self.coords = colored_point.copy()
            self.color = self.coords.pop()
            
        left = None
        right = None
        box = None
        weight = None
        
    class BoundingBox():
        def __init__(self, min_coords, max_coords):
            self.min_coords = min_coords.copy()
            self.max_coords = max_coords.copy() 
            
    # returns a list of nodes which represent colored disjoint boxes from the points in dataset
    def transform_dataset(self, dataset):
        if self.dataset_dim == 2:
            # create a dict of size num_colors, each element containing a list of one distinct color
            color_list_dict = dict()
            for i in range(len(dataset)):
                color = dataset[i][-1]
                # if color is in color dictionary, append point
                if color in color_list_dict.keys():
                    color_list_dict[color].append(dataset[i])
                # else, create a list with point
                else:
                    color_list_dict[color] = [dataset[i]]
            
            # for each color create a list ordered by the x coordinate of the dataset
            transformed_dataset = list()
            for color in color_list_dict:
                color_list = color_list_dict[color].copy()
                self.sort_dataset(color_list, 0, len(color_list) - 1, 0)
                
                # create three dimensional nodes representing colored disjoint boxes
                # transform minimum point
                v = self.Node([color_list[0][0], color_list[0][1], np.inf, color_list[0][2]])
                transformed_dataset.append(v)
                # transform points with a y_min smaller than the previously transformed point
                y_min = color_list[0][1]
                for i in range(1, len(color_list)):
                    if color_list[i][1] < y_min:
                        v = self.Node([color_list[i][0], color_list[i][1], y_min, color_list[i][2]])
                        transformed_dataset.append(v)
                        y_min = color_list[i][1]
            self.kdtree_dim = 3
            
        return transformed_dataset
    
    # returns the root of KD tree
    # dataset: list of colored nodes
    # depth: depth of tree
    # box: bounding box of root node
    def build_kdtree(self, dataset, depth = None, box = None):
        # at root, set depth to 0
        if depth is None:
            depth = 0
            
        # at root, set bounding box to range of dataset
        if box is None:                    
            min_coords = list(range(self.kdtree_dim))
            max_coords = list(range(self.kdtree_dim))
            
            # find max and min for every dimension
            for dim in range(self.kdtree_dim):
                min_coords[dim] = np.inf
                max_coords[dim] = -np.inf
                # search through every point in dataset
                for i in range(len(dataset)):
                    if dataset[i].coords[dim] <= min_coords[dim]:
                        min_coords[dim] = dataset[i].coords[dim]
                        
                    if dataset[i].coords[dim] >= max_coords[dim]:
                        max_coords[dim] = dataset[i].coords[dim]
                        
            box = self.BoundingBox(min_coords, max_coords)
          
        # base case, dataset has one node v
        # set v's box to itself
        # set v's weight to the weight of its color
        if len(dataset) == 1:
            v = self.Node(dataset[0].coords + [dataset[0].color])
            v.box = box
            v.weight = self.color_weight_dict[v.color]
            v.left = None
            v.right = None
            
        # dataset has more than one node
        else:         
            # split dataset on median node on curr_dim
            curr_dim = depth % self.kdtree_dim
            self.sort_dataset(dataset, 0, len(dataset) - 1, curr_dim)  
                      
            if len(dataset) % 2 == 0:
                mid = (len(dataset) // 2) - 1
            else:
                mid = len(dataset) // 2
                
            dataset_left = dataset[:mid + 1]
            dataset_right = dataset[mid + 1:]
            
            # set v as the median internal node
            # recursively call buildRangeTree on dataset's left & right sublists to assign v's left & right children 
            v = self.Node(dataset[0].coords + [dataset[0].color])
            v.box = box

            box_left = self.BoundingBox(v.box.min_coords, v.box.max_coords)
            box_left.max_coords[curr_dim] = v.coords[curr_dim]
            
            box_right = self.BoundingBox(v.box.min_coords, v.box.max_coords)
            box_right.min_coords[curr_dim] = v.coords[curr_dim]
            
            v.left = self.build_kdtree(dataset_left, depth + 1, box_left)
            v.right = self.build_kdtree(dataset_right, depth + 1, box_right)
            
            # assign v's weight to the sum of its childrens weights
            v.weight = v.left.weight + v.right.weight
                
        return v
    
    # sort_dataset implementation to sort points in dataset
    def sort_dataset(self, dataset, low, high, dim):
        if low < high:
            pi = self.partition(dataset, low, high, dim)
            self.sort_dataset(dataset, low, pi, dim)
            self.sort_dataset(dataset, pi + 1, high, dim)
    
    # helper function to find partition in sort_dataset
    def partition(self, dataset, low, high, dim):
        if isinstance(dataset[0], self.Node):
            pivot = dataset[(low + high) // 2].coords[dim]
        else:
            pivot = dataset[(low + high) // 2][dim]
        i = low - 1
        j = high + 1
        while True:
            while True:
                i = i + 1
                if isinstance(dataset[0], self.Node):
                    if dataset[i].coords[dim] >= pivot:
                        break
                else:
                    if dataset[i][dim] >= pivot:
                        break
            while True:
                j = j - 1
                if isinstance(dataset[0], self.Node):
                    if dataset[j].coords[dim] <= pivot:
                        break
                else:
                    if dataset[j][dim] <= pivot:
                        break
            if i < j:
                (dataset[i], dataset[j]) = (dataset[j], dataset[i])
            else:
                return j
    
    # returns a random sample within the range 
    # orthant: a point of type {ai,...,ad} which implicitly defines the region [-inf, ai] x ... x [-inf, ad]
    def query_random_node(self, orthant):
        C = self.find_canonical_nodes(orthant, self.root)
        
        # return if C is empty
        if not C:
            # print('no canonical nodes found')
            return None
        
        # find canonical node with greatest key, c_max
        c_max = C[0]
        c_max_key = np.random.random() ** (1 / c_max.weight)
        
        # loop from second node to end of C
        # find the canonical node with the greatest key in C and assign to c_max
        for i in range(1, len(C)):
            c_curr = C[i]
            c_curr_key = np.random.random() ** (1 / c_curr.weight)
            # replace c_max if the current canonical node has a greater key
            if c_curr_key > c_max_key:
                c_max = c_curr
                c_max_key = c_curr_key
                
        # traverse child of c_max with greatest key until reach leaf
        v = c_max
        while v.left is not None and v.right is not None:
            if np.random.random() ** (1 / v.left.weight) > np.random.random() ** (1 / v.right.weight):
                v = v.left
            else:
                v = v.right
        
        return v
    
    # returns a list of all canonical nodes within the range 
    # min_coords: a list of minimum boundaries in all dimensions
    # max_coords: a list of maximum boundaries in all dimensions
    # root: root of kdtree or subtree in kdtree
    def find_canonical_nodes(self, orthant, root):               
        # create an empty list to contain all canonical nodes within range
        C = list()
        
        # if root is a leaf, check if root's coordinate intersects range
        if root.left is None and root.right is None:
            # append canonical node if coordinate intersects range
            if self.kdtree_dim == 3:                
                if root.coords[0] <= orthant[0] and root.coords[1] <= orthant[1] and root.coords[2] > orthant[1]:
                    C.append(root)
                else:
                    pass
            
        # if root is not a leaf
        else:
            if self.kdtree_dim == 3:              
                # root.box has no intersection with orthant
                if root.box.min_coords[0] > orthant[0] or root.box.min_coords[1] > orthant[1] or root.box.max_coords[2] <= orthant[1]:
                    return C
                
                # root.box fully intersects orthant
                elif root.box.max_coords[0] <= orthant[0] and root.box.max_coords[1] <= orthant[1] and root.box.min_coords[2] > orthant[1]: 
                    C.append(root)
                    
                # root.box partially intersects orthant
                else:
                    C_left = self.find_canonical_nodes(orthant, root.left)
                    C_right = self.find_canonical_nodes(orthant, root.right)
                    
                    if C_left:
                        C = C + C_left
                    if C_right:
                        C = C + C_right
        return C