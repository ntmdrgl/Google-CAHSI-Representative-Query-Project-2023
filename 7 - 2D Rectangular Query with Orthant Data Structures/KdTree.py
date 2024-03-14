# -*- coding: utf-8 -*-
"""
Created on March 13, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal

Objective:
 - KdTree will be used to implement:
   1. 3-sided query (6D points representing cubes)
   2. 3-sided emptiness (3D points)
    
 - Implement a data structure which can report colors from a 3-sided query
   - Nodes represent colored disjoint cubes
   - Query ranges represent points intersecting cubes
   
 - Implement a data structure which can report emptiness from a 3-sided query
   - Nodes represent points of homologous colors
   - Query ranges represent maximally empty orthants
"""
import numpy as np
import time
import sys

class KdTree():
    def __init__(self, dataset, color_weights):
        if len(dataset[0]) == 4:
            self.num_dim = 3
        if len(dataset[0]) == 9:
            self.num_dim = 6                   # number of dimensions in points
        self.num_colors = len(color_weights)   # number of colors in points
        self.color_weights = color_weights     # dictionary of colors mapped to weights
        self.root = self.build_kdtree(dataset) # root of kdtree
        
    class Node():
        def __init__(self, colored_point):
            if len(colored_point) == 4:
                self.point = colored_point.copy()
                self.color = self.point.pop()
            
            if len(colored_point) == 9:
                self.point = colored_point[0:7]
                self.original_point = colored_point[7:]
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
    
    def report_emptiness(self, min_point, max_point):
        canonical_nodes = self.report_canonical_nodes(self.root, min_point, max_point, [])
        

        if len(canonical_nodes) == 0:
            return True
        else:
            return False
        
    def report_colors(self, min_point, max_point):
        # C = self.report_canonical_nodes(self.root, min_point, max_point, [])
        C = self.find_canonical_nodes(self.root, min_point, max_point, [])
        return C

    def report_canonical_nodes(self, root, min_point, max_point, canonical_nodes=[]):
        x = root.min_point
        y = root.max_point
        # search leaf node
        if root.left is None and root.right is None:
            if all(min_point[i] < root.point[i] < max_point[i] for i in range(self.num_dim)):
                canonical_nodes.append(root)
        # search internal node
        else:
            x = root.left.min_point
            y = root.left.max_point
            # left fully intersects
            if all(min_point[i] < root.left.min_point[i] and root.left.max_point[i] < max_point[i] for i in range(self.num_dim)):
                canonical_nodes.append(root)
            # left partially intersects
            elif not any(root.left.min_point[i] > max_point[i] or root.left.max_point[i] < min_point[i] for i in range(self.num_dim)):
                self.report_canonical_nodes(root.left, min_point, max_point, canonical_nodes)
            
            x = root.right.min_point
            y = root.right.max_point
            # repeat on right side
            if all(min_point[i] < root.right.min_point[i] and root.right.max_point[i] < max_point[i] for i in range(self.num_dim)):
                canonical_nodes.append(root)
            elif not any(root.right.min_point[i] > max_point[i] or root.right.max_point[i] < min_point[i] for i in range(self.num_dim)):
                self.report_canonical_nodes(root.right, min_point, max_point, canonical_nodes)
            
        return canonical_nodes
    
    def find_canonical_nodes(self, root, min_point, max_point, canonical_nodes=[]):          
        # if root is a leaf, check if root's coordinate intersects range
        if root.left is None and root.right is None:
            coordinate_intersects = True
            
            for dim in range(self.num_dim):
                if root.point[dim] < min_point[dim] or root.point[dim] > max_point[dim]:
                    coordinate_intersects = False
                    break
                
            # append canonical node if coordinate intersects range
            if coordinate_intersects:
                canonical_nodes.append(root)
            else:
                pass
            
        # if root is not a leaf
        else:
            # check whether root's box does not intersect range or is fully contained in range
            box_fully_intersects = True
            
            for dim in range(self.num_dim):
                # if root's box does not intersect range, return
                if root.min_point[dim] > max_point[dim] or root.max_point[dim] < min_point[dim]:
                    return canonical_nodes
                
                # if root's box is not contained in range, break lsoop
                if root.min_point[dim] < min_point[dim] or root.max_point[dim] > max_point[dim]:
                    box_fully_intersects = False
                    break
            
            # if root's box fully intersects range, append root to list
            if box_fully_intersects:
                canonical_nodes.append(root)
                
            # if root's box partially intersects range, search root's left and right
            else:
                self.find_canonical_nodes(root.left, min_point, max_point, canonical_nodes)
                self.find_canonical_nodes(root.right, min_point, max_point, canonical_nodes)

        return canonical_nodes
