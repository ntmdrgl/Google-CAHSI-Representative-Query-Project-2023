# -*- coding: utf-8 -*-
"""
Created on February 7, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal

"""
import numpy as np

class OrthogonalSearchTree():
    def __init__(self, dataset, color_weights):
        # if len(dataset[0]) == 4:
        #     self.num_dim = 3
        # elif len(dataset[0]) == 9:
        self.num_dim = 6                   # number of dimensions in points
        self.num_colors = len(color_weights)   # number of colors in points
        self.color_weights = color_weights     # dictionary of colors mapped to weights
        self.node_id = 0
        
        self.root = self.build_kdtree(dataset) # root of kdtree
        
    def get_node_id(self):
        self.node_id += 1
        return self.node_id
        
    class Node():
        def __init__(self, colored_point):
            # if len(colored_point) == 4:
            #     self.point = colored_point.copy()
            #     self.color = self.point.pop()
            
            if len(colored_point) == 9:
                self.point = colored_point[0:7]
                self.original_point = colored_point[7:]
                self.color = self.point.pop()
            else:
                print("ERROR, wrong number of args")
        
        left = None      # left child
        right = None     # right child
        min_point = None # min point of bounding box 
        max_point = None # max point of bounding box
        weight = None    # weight of subtree rooted at self  
        count = None     # number of leaves in subtree rooted at self
        node_id = 0
    
    class BoundingBox():
        def __init__(self, min_point, max_point):
            self.min_point = min_point.copy()
            self.max_point = max_point.copy()
    
    def build_kdtree(self, dataset, depth = 0, box = None):
        # at root, set bounding box to range of dataset
        if box is None:                    
            min_point = list(range(self.num_dim))
            max_point = list(range(self.num_dim))
            
            # find min and max for every dimension
            for dim in range(self.num_dim):
                min_point[dim] = np.inf
                max_point[dim] = -np.inf
                # search through every point in dataset
                for i in range(len(dataset)):
                    if dataset[i][dim] <= min_point[dim]:
                        min_point[dim] = dataset[i][dim]
                        
                    if dataset[i][dim] >= max_point[dim]:
                        max_point[dim] = dataset[i][dim]
                        
            box = self.BoundingBox(min_point, max_point)
        
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
            v.node_id = self.get_node_id()
            
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

            box_left = self.BoundingBox(v.box.min_point, v.box.max_point)
            box_left.max_point[curr_dim] = v.point[curr_dim]
            
            box_right = self.BoundingBox(v.box.min_point, v.box.max_point)
            box_right.min_point[curr_dim] = v.point[curr_dim]
            
            v.left = self.build_kdtree(dataset_left, depth + 1, box_left)
            v.right = self.build_kdtree(dataset_right, depth + 1, box_right)
            
            # assign v's weight to the sum of its childrens weights
            v.weight = v.left.weight + v.right.weight
            v.count = v.left.count + v.right.count # + 1          
            v.node_id = self.get_node_id()
            
        return v
        
    # returns a random sample within the range 
    def report_colors(self, min_point, max_point):
        # C = self.find_canonical_nodes(min_point, max_point, self.root)
        C = self.report_canonical_nodes(min_point, max_point, self.root)
        return C
    
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
                if root.box.min_point[dim] > max_point[dim] or root.box.max_point[dim] < min_point[dim]:
                    return C
                
                # if root's box is not contained in range, break loop
                if root.box.min_point[dim] < min_point[dim] or root.box.max_point[dim] > max_point[dim]:
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
            if all(min_point[i] <= root.box.min_point[i] and root.box.max_point[i] <= max_point[i] for i in range(self.num_dim)):
                # print("  Full")
                C.append(root)
            # partially intersects
            elif not any(root.box.min_point[i] > max_point[i] or root.box.max_point[i] < min_point[i] for i in range(self.num_dim)):
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