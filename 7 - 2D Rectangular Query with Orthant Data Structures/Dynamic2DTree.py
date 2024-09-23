# -*- coding: utf-8 -*-
"""
Created on: May 9, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal

@author: nthnl
"""

import numpy as np
import time

class DTree():
    def __init__(self, dataset):
        self.num_dim = 2                       # number of dimensions in points
        self.root = self.build_kdtree(dataset) # root of kdtree
        # self.current_n = self.root.count
        
    class Node():
        def __init__(self, colored_point):
            (self.point, self.tup) = colored_point
            self.point = self.point.copy()
            self.color = self.point.pop()
        
        left = None      # left child
        right = None     # right child
        min_point = None # min point of bounding box 
        max_point = None # max point of bounding box
        # weight = None    # weight of subtree rooted at self  
        count = None     # number of leaves in subtree rooted at self
        is_deleted = False
        
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
                    (point, tup) = dataset[i] 
                    if point[axis] <= min_point[axis]:
                        min_point[axis] = point[axis]
                        
                    if point[axis] >= max_point[axis]:
                        max_point[axis] = point[axis]
        
        # create leaf
        if len(dataset) == 1: 
            v = self.Node(dataset[0])
            v.min_point = min_point
            v.max_point = max_point
            # v.weight = self.color_weights[v.color]
            v.count = 1
        # create internal node
        else:
            axis = depth % self.num_dim
            
            # find median point
            dataset.sort(key=lambda p: p[0][axis])
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
            max_left = max_point.copy()
            max_left[axis] = v.point[axis] 
            min_right = min_point.copy()
            min_right[axis] = v.point[axis] 
            max_right = v.max_point
            
            v.left = self.build_kdtree(dataset_left, depth + 1, min_left, max_left)
            v.right = self.build_kdtree(dataset_right, depth + 1, min_right, max_right)
            # v.weight = v.left.weight + v.right.weight
            v.count = v.left.count + v.right.count
            
        return v

    def report_leaves(self, root, leaves=[]):
        if root is None:
            return
        if root.left is None and root.right is None:
            leaves.append(root)
        else: 
            self.report_leaves(root.left, leaves)
            self.report_leaves(root.right, leaves)
        return leaves

    def insert(self, point):
        pass
        
    def delete(self, root, point, axis=0):
        pass
        # if root.point[axis] == point[axis]:
        #     if root.left is None and root.right is None:
        #         root.is_deleted = True
        #     else:
        #         print(root.left.point, root.left.point)
        # elif root.point[axis] < point[axis]:
        #     self.delete(self, root, point, axis=0)
        
    def query_range_report(self, min_point, max_point):
        if self.root is None:
            return None
        
        canonical_nodes = self.report_canonical_nodes(min_point, max_point, self.root)
        # canonical_nodes = self.find_canonical_nodes(min_point, max_point, self.root)
        if not canonical_nodes:
            return None
        
        report_points = list()
        for c in canonical_nodes:
            report_c = list()
            report_c = self.query_range_report_help(c)
            if report_c:
                report_points += report_c
            
        return report_points
    
    def query_range_report_help(self, c):
        report_c = list()
        if c is None:
            return None
        if c.left is None and c.right is None:
            report_c.append(c)
        else:
            report_c_left = self.query_range_report_help(c.left)
            report_c_right = self.query_range_report_help(c.right)
            if report_c_left:
                report_c += report_c_left
            if report_c_right:
                report_c += report_c_right
        return report_c        
        
    # returns a list of all canonical nodes within the range 
    # root: root of kdtree or subtree in kdtree
    def find_canonical_nodes(self, min_point, max_point, root):          
        # create an empty list to contain all canonical nodes within range
        C = list()
        
        # if root is a leaf, check if root's coordinate intersects range
        if root.left is None and root.right is None:
            coordinate_intersects = True
            
            for dim in range(self.num_dim):
                if root.point[dim] < min_point[dim] or root.point[dim] > max_point[dim]:
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
                if root.min_point[dim] >= max_point[dim] or root.max_point[dim] <= min_point[dim]:
                    return C
                
                # if root's box is not contained in range, break loop
                if root.min_point[dim] < min_point[dim] or root.max_point[dim] > max_point[dim]:
                    box_fully_intersects = False
                    break
            
            # if root's box fully intersects range, append root to list
            if box_fully_intersects:
                # print("fully intersects")
                C.append(root)
                
            # if root's box partially intersects range, search root's left and right
            else:
                C_left = self.find_canonical_nodes(min_point, max_point, root.left)
                C_right = self.find_canonical_nodes(min_point, max_point, root.right)
                
                if C_left:
                    C = C + C_left
                if C_right:
                    C = C + C_right
        
        return C
    
    def report_canonical_nodes(self, min_point, max_point, root):
        # create an empty list to contain all canonical nodes within range
        C = list()
        
        # search leaf node
        if root.left is None and root.right is None:
            # print("  Leaf")
            # print("  x", min_point[0], root.point[0], max_point[0])
            # print("  y", min_point[1], root.point[1], max_point[1])
            if all(min_point[i] <= root.point[i] <= max_point[i] for i in range(self.num_dim)):
            # if not any(root.point[i] > max_point[i] or root.point[i] < min_point[i] for i in range(self.num_dim)):
                # print("  Leaf added")
                C.append(root)
            else:
                # print("  Leaf not in range")
                pass
        # search internal node
        else:
            # print("  x", min_point[0], root.min_point[0], root.max_point[0], max_point[0])
            # print("  y", min_point[1], root.min_point[1], root.max_point[1], max_point[1])
            # fully intersects
            if all(min_point[i] <= root.min_point[i] and root.max_point[i] <= max_point[i] for i in range(self.num_dim)):
                # print("  Full")
                C.append(root)
            # partially intersects
            elif not any(root.min_point[i] > max_point[i] or root.max_point[i] < min_point[i] for i in range(self.num_dim)):
                # print("  Partial")
                C_left = self.report_canonical_nodes(min_point, max_point, root.left)
                C_right = self.report_canonical_nodes(min_point, max_point, root.right)
                
                if C_left:
                    C = C + C_left
                if C_right:
                    C = C + C_right
            else:
                # print("  No intersect")
                pass
                    
        return C