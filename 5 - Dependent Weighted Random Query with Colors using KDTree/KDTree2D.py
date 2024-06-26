# -*- coding: utf-8 -*-
"""
Created on: November 16, 2023
Authors: Nathaniel Madrigal, Alexander Madrigal

Objective:
- Create a KDTree structure which queries a random point within a rectangular range. Points are queried
  proportional to the weight of their associated color.
  
- The output of a query search is dependent to the rectangular range (searching the same range returns the
  same output)
    
Notable Class Functions:
- build_kdtree: Given a list of points, recursively builds the KDTree by splitting the inputted list by the 
  median point on the current dimension where the recursive function is called on the two sublists. Each recursive 
  call proceeds to split the list based on values of the next dimension (wrap around). At the base case where the 
  list has one element, a leaf node is created with a 'key' is calculated of the form: {u ** [1 / w]} where u is a 
  random number from 0-1 and w is the weight of the node's 'color'. Each leqf node will also contain a 'maxnode'
  pointer to itself. When creating an internal node, the internal node's 'key' is set to greatest 'key' out of
  its two children. The internal node's 'maxnode' pointer will be the same as the 'maxnode' of the child with
  the greatest 'key'. The function returns the root of the kdtree.
  
- find_canonical_nodes: Given the root of a KDTree and rectangular region, recursively searches for nodes which 
  its children are fully contained in the rectangular region called canonical nodes. The base case where root is
  a leaf node simply checks if the node's coordinates are within the rectangular region and adds the root node to 
  a list of canonical nodes if so. When the root is not a leaf the function must check if the root's 'box' 1. fully 
  interests, 2. has no intersect, or 3. partially intersects with the rectangular region. When root's 'box' fully 
  intersects, the root is added to the list of canonical nodes. When root's 'box' has no intersection, function 
  returns. In the recursive case where a partial intersect is found, a recursive function is called on the root's 
  two children. The function returns a list containing all canonical nodes.
  
- query_random_sample: First calls the find_canonical_nodes function. Given a list of canonical nodes, finds
  the canonical node with the greatest key and returns that node's 'maxnode' pointer. 

    
"""

import numpy as np

class KDTree():        
    def __init__(self, dataset, color_weight_dict):
        self.max_dimension = 2
        self.color_weight_dict = color_weight_dict
        self.root = self.build_kdtree(dataset)   
        self.color_counts = list(range(len(color_weight_dict)))
    
    class Node():
        def __init__(self, colored_coord):
            self.coord = colored_coord.copy()
            self.color = self.coord.pop()
            self.color = str(self.color)
            
        left = None
        right = None
        box = None
        key = None
        maxNode = None # pointer to child with greatest key
        
    class BoundingBox():
        def __init__(self, min_coords, max_coords):
            self.min_coords = min_coords.copy()
            self.max_coords = max_coords.copy() 
    
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
                    if dataset[i][dim] < min_coords[dim]:
                        min_coords[dim] = dataset[i][dim]
                        
                    if dataset[i][dim] > max_coords[dim]:
                        max_coords[dim] = dataset[i][dim]
                        
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

            box_left = self.BoundingBox(v.box.min_coords, v.box.max_coords)
            box_left.max_coords[curr_dim] = v.coord[curr_dim]
            box_right = self.BoundingBox(v.box.min_coords, v.box.max_coords)
            box_right.min_coords[curr_dim] = v.coord[curr_dim]
            
            
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
     
    # sort_dataset implementation to sort points in dataset
    def sort_dataset(self, dataset, low, high, dim):
        if low < high:
            pi = self.partition(dataset, low, high, dim)
            self.sort_dataset(dataset, low, pi, dim)
            self.sort_dataset(dataset, pi + 1, high, dim)
    
    # returns a random sample within the range 
    # min_coords: a list of minimum boundaries in all dimensions
    # max_coords: a list of maximum boundaries in all dimensions
    def query_random_sample(self, min_coords, max_coords):
        C = self.find_canonical_nodes(min_coords, max_coords)
        
        # return if C is empty
        if not C:
            return None
        
        self.update_color_counts(C)
        
        # initialize c_max as first element in list
        c_max = C[0]
        
        # assign max_node to canonical node with the greatest key
        for c in  C:
            if c.key > c_max.key:
                c_max = c
                
        # return the node stored at c_max's maxNode 
        return c_max.maxNode
    
    # updates list containing counts of colors under a list of canonical nodes
    # C: canonical nodes
    def update_color_counts(self, C):
        for node in C:
            self.update_color_counts_util(node)
        
    def update_color_counts_util(self, node):
        if node is None:
            return
        
        # increment color counts if node is leaf
        if node.left is None and node.right is None:
            self.color_counts[int(node.color) - 1] += 1
            return
            
        self.update_color_counts_util(node.left)
        self.update_color_counts_util(node.right)
        
    # returns a list of all canonical nodes within the range 
    # min_coords: a list of minimum boundaries in all dimensions
    # max_coords: a list of maximum boundaries in all dimensions
    # root: root of kdtree or subtree in kdtree
    def find_canonical_nodes(self, min_coords, max_coords, root = None):
        if len(min_coords) != self.max_dimension or len(max_coords) != self.max_dimension:
            raise Exception('Incorrect number of dimensions in list argument')
        
        if root is None:
            root = self.root
            
        # create an empty list to contain all canonical nodes within range
        C = list()
        
        # if root is a leaf, check if root's coordinate intersects range
        if root.left is None and root.right is None:
            coordinate_intersects = True
            
            for dim in range(self.max_dimension):
                if root.coord[dim] < min_coords[dim] or root.coord[dim] > max_coords[dim]:
                    coordinate_intersects = False
                    break
                
            # append canonical node if coordinate intersects range
            if coordinate_intersects:
                C.append(root)
            else:
                return C
            
        # if root is not a leaf
        else:
            # check whether root's box does not intersect range or is fully contained in range
            box_fully_intersects = True
            
            for dim in range(self.max_dimension):
                # if root's box does not intersect range, return
                if root.box.min_coords[dim] > max_coords[dim] or root.box.max_coords[dim] < min_coords[dim]:
                    return C
                
                # if root's box is not contained in range, break loop
                if root.box.min_coords[dim] < min_coords[dim] or root.box.max_coords[dim] > max_coords[dim]:
                    box_fully_intersects = False
                    break
            
            # if root's box fully intersects range, append root to list
            if box_fully_intersects:
                C.append(root)
            
            # if root's box partially intersects range, search root's left and right
            else:          
                C_left = self.find_canonical_nodes(min_coords, max_coords, root.left)
                C_right = self.find_canonical_nodes(min_coords, max_coords, root.right)
                
                if C_left:
                    C = C + C_left
                if C_right:
                    C = C + C_right
        
        return C
        
            
        
    

