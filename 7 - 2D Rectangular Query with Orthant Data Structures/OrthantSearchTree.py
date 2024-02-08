# -*- coding: utf-8 -*-
"""
Created on February 7, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal

"""
import numpy as np

class OrthantSearchTree():
    # d dimensional orthant searches using 2*d dimensional kdtree 
    # dataset should already be in 2*d dimensions
    def __init__(self, dataset, color_weights):
        self.num_dim = len(dataset[0]) - 1
        self.num_colors = len(color_weights)
        
        self.color_weights = color_weights.copy()
        self.root = self.build_kdtree(dataset)
        
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
    
    def build_kdtree(self, dataset, depth = 0, box = None):
        # at root, set bounding box to range of dataset
        if box is None:                    
            min_coords = list(range(self.num_dim))
            max_coords = list(range(self.num_dim))
            
            # find max and min for every dimension
            for dim in range(self.num_dim):
                min_coords[dim] = np.inf
                max_coords[dim] = -np.inf
                # search through every point in dataset
                for i in range(len(dataset)):
                    if dataset[i][dim] <= min_coords[dim]:
                        min_coords[dim] = dataset[i][dim]
                        
                    if dataset[i][dim] >= max_coords[dim]:
                        max_coords[dim] = dataset[i][dim]
                        
            box = self.BoundingBox(min_coords, max_coords)
        
        # base case, dataset has one node v
        # set v's box to itself
        # set v's weight to the weight of its color
        if len(dataset) == 1:
            v = self.Node(dataset[0])
            v.weight = self.color_weights[v.color]
            v.box = box
            
        # dataset has more than one node
        else:         
            # split dataset on median node on curr_dim
            curr_dim = depth % self.num_dim
            self.sort_dataset(dataset, 0, len(dataset) - 1, curr_dim)  
                      
            if len(dataset) % 2 == 0:
                mid = (len(dataset) // 2) - 1
            else:
                mid = len(dataset) // 2
                
            dataset_left = dataset[:mid + 1]
            dataset_right = dataset[mid + 1:]
            
            # set v as the median internal node
            # recursively call buildRangeTree on dataset's left & right sublists to assign v's left & right children 
            v = self.Node(dataset[mid])
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
        
    # returns a random sample within the range 
    # orthant: a point of type {ai,...,ad} which implicitly defines the region [-inf, ai] x ... x [-inf, ad]
    def query_random_sample(self, orthant):
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
    # root: root of kdtree or subtree in kdtree
    def find_canonical_nodes(self, orthant, root):               
        # create an empty list to contain all canonical nodes within range
        C = list()
        
        # if root is a leaf, check if root's coordinate intersects range
        if root.left is None and root.right is None:
            # append canonical node if coordinate intersects range                
            intersects = True
            for dim in range(self.num_dim // 2):
                if not (root.coords[dim*2] <= orthant[dim] or root.coords[dim*2+1] >= orthant[dim]):
                    intersects = False
            if intersects:
                C.append(root)
            
        # if root is not a leaf
        else:             
            # root.box has no intersection with orthant
            for dim in range(self.num_dim // 2):
                if root.box.min_coords[dim*2] > orthant[dim] or root.box.max_coords[dim*2+1] < orthant[dim]:
                    return C
            
            # root.box fully intersects orthant
            intersects = True
            for dim in range(self.num_dim // 2):
                if not (root.coords[dim*2] <= orthant[dim] or root.coords[dim*2+1] >= orthant[dim]):
                    intersects = False
            if intersects:
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
    
