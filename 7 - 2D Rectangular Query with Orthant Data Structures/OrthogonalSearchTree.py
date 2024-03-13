# -*- coding: utf-8 -*-
"""
Created on February 7, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal

"""
import numpy as np

class OrthogonalSearchTree():
    def __init__(self, dataset, color_weights):
        self.num_dim = 6
        self.num_colors = len(color_weights)
        
        self.color_weights = color_weights
        self.last_id = 0
        self.root = self.build_kdtree(dataset)
            
    class Node():
        def __init__(self, point):
            self.coords = point.copy()
            self.color = self.coords.pop()
            
            self.isTypeLeft = self.coords.pop()
            if self.isTypeLeft:
                self.orig_coords = [self.coords[1], self.coords[5]]
            else:
                self.orig_coords = [self.coords[1], self.coords[4]]
        
        isTypeLeft = None
        orig_coords = None
        
        left = None
        right = None
        box = None
        weight = None
        search_weight = None
        count = None
        node_id = None
    
    def get_id(self):
        return self.last_id
        self.last_id += 1
        
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
        
        if len(dataset) <= 0:
            return None
        
        # base case, dataset has one node v
        # set v's box to itself
        # set v's weight to the weight of its color
        if len(dataset) == 1:
            v = self.Node(dataset[0])
            v.weight = self.color_weights[v.color]
            v.count = 1
            v.box = box
            v.node_id = self.get_id()
            
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
            v.count = v.left.count + v.right.count + 1
            v.node_id = self.get_id()              
            
        return v
        
    # returns a random sample within the range 
    def report_colors(self, min_coords, max_coords):
        C = self.find_canonical_nodes(min_coords, max_coords, self.root)
        return C
    
    # returns a list of all canonical nodes within the range 
    # root: root of kdtree or subtree in kdtree
    def find_canonical_nodes(self, min_coords, max_coords, root):          
        # create an empty list to contain all canonical nodes within range
        C = list()
        
        # if root is a leaf, check if root's coordinate intersects range
        if root.left is None and root.right is None:
            coordinate_intersects = True
            
            for dim in range(self.num_dim):
                if root.coords[dim] < min_coords[dim] or root.coords[dim] > max_coords[dim]:
                    coordinate_intersects = False
                    break
                
            # append canonical node if coordinate intersects range
            if coordinate_intersects:
                C.append(root)
                # print("leaf intersects")
            else:
                pass
            
        # if root is not a leaf
        else:
            # check whether root's box does not intersect range or is fully contained in range
            box_fully_intersects = True
            
            for dim in range(self.num_dim):
                # if root's box does not intersect range, return
                if root.box.min_coords[dim] > max_coords[dim] or root.box.max_coords[dim] < min_coords[dim]:
                    return C
                
                # if root's box is not contained in range, break loop
                if root.box.min_coords[dim] < min_coords[dim] or root.box.max_coords[dim] > max_coords[dim]:
                    box_fully_intersects = False
                    break
            
            # if root's box fully intersects range, append root to list
            if box_fully_intersects:
                # print("fully intersects")
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