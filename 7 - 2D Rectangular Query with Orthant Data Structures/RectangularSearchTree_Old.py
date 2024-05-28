# -*- coding: utf-8 -*-
"""
Created on February 7, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal

"""

import OrthogonalSearchTree_Old as OSTree
import Dynamic2DTree as DTree
import KdTree
import numpy as np
import time
import sys

class RSTree():
    def __init__(self, dataset, color_weights, x_const):
        self.num_dim = 2                            # number of dimensions in points
        self.num_colors = len(color_weights)        # number of colors in points
        self.color_weights = color_weights.copy()   # dictionary of colors mapped to weights
        self.x_const = x_const
        
        self.root = self.build_tree(dataset)        # root of tree
        
        self.light_count = 0
        self.heavy_count = 0
        self.num_counts = 0
        self.sum_counts = 0
        self.avg_count = 0
        
        self.color_freqs = [0,0,0,0,0]
        
        
    class Node():
        def __init__(self, point):
            self.point = point.copy()
            self.color = self.point.pop()
            
        left = None          # left child
        right = None         # right child
        weight = None        # weight of subtree rooted at self  
        search_weight = None # temporary weight of node after intersection removal
        count = None         # number of leaves in subtree rooted at self
        aux_left = None      # 3-sided query tree on type-left points 
        aux_right = None     # 3-sided query tree on type-right points
        
        matrix = None
        left_to_idx = None
        right_to_idx = None
    
    # tree sorted on y-coordinates (axis=1)
    def build_tree(self, dataset, depth=0):
        axis = 1
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
            v.left = self.build_tree(dataset_left, depth + 1)
            v.right = self.build_tree(dataset_right, depth + 1)
            v.weight = v.left.weight + v.right.weight
            v.count = v.left.count + v.right.count
            
            # transform left and right child's dataset
            # and create 3-sided auxillary trees
            transform_left = self.transform_dataset(dataset_left, True)
            transform_right = self.transform_dataset(dataset_right, False)
            # v.aux_left = KdTree.KdTree(transform_left, self.color_weights)
            # v.aux_right = KdTree.KdTree(transform_right, self.color_weights)
            v.aux_left = OSTree.OrthogonalSearchTree(transform_left, self.color_weights)
            v.aux_right = OSTree.OrthogonalSearchTree(transform_right, self.color_weights)
            
            v.matrix = self.build_matrix(v)
            
        return v
        
    # inputs dataset and returns transformed dataset of decomposed colored boxes
    def transform_dataset(self, dataset, isTypeLeft):
        # generate lists separated by colors stored in a dictionary
        color_buckets = dict()
        for i in range(len(dataset)):           
            color = dataset[i][-1]
            if not color in color_buckets.keys():
                color_buckets[color] = [dataset[i]]
            else:
                color_buckets[color].append(dataset[i])
            
        # create disjoint cubes for each color and append to transformed dataset 
        transformed_dataset = list()
        for color in color_buckets:
            # transform points from (x, y) to (x, y, z) where y is duplicate x
            color_list = color_buckets[color]
            for it, point in enumerate(color_list):
                color_list[it] = [point[0], point[0], point[1], point[-1]]
            
            # append colored boxes to transformed dataset
            # additive to not override transformed dataset over many colors
            
            # skyline_points = self.convert_to_skyline(color_list, self.color_weights, isTypeLeft)   
            # self.convert_to_boxes(skyline_points, isTypeLeft, transformed_dataset)
            
            transformed_dataset = self.report_meo_to_boxes(color_list, isTypeLeft)
            
        
        return transformed_dataset
    
    # inputs a list of colored points and returns sublist of maximally empty orthants
    def convert_to_skyline(self, color_list, color_weights, isTypeLeft):
        # find skyline points using 3-sided emptiness queries
        skyline_points = list()
        emptiness_tree = KdTree.KdTree(color_list, self.color_weights)
        for point in color_list:
            min_point = None
            max_point = None                
            if isTypeLeft:
                min_point = [point[0], -np.inf,  point[2]]
                max_point = [np.inf,   point[1], np.inf  ]
            else:
                min_point = [point[0], -np.inf,  -np.inf ]
                max_point = [np.inf,   point[1], point[2]]
            
            if emptiness_tree.report_emptiness(min_point, max_point):
                skyline_points.append(point)
             
        if len(skyline_points) == 0:
            print("NO SKYLINE FOUND, BEFORE:(len,list)",len(color_list), color_list)
        
        return skyline_points
        
    # inputs skyline points on dataset and updates new boxes into transformed dataset
    def convert_to_boxes(self, skyline_points, isTypeLeft, transformed_dataset=[]):
        # transform 3d maximally empty points into 6d disjoint cubes             
        skyline_points.sort(key=lambda p: p[0])
        skyline_points.reverse()
        
        for it, p in enumerate(skyline_points):
            if it == 0:
                if isTypeLeft:
                    transformed_dataset.append([-np.inf, p[0], p[1], np.inf, -np.inf, p[2], p[-1], p[0], p[2]])
                else:
                    transformed_dataset.append([-np.inf, p[0], p[1], np.inf, p[2], np.inf, p[-1], p[0], p[2]])
                continue
            
            prev = skyline_points[it - 1]
            if isTypeLeft:
                # create y max bound if under previous point (from z)
                if p[2] < prev[2]:
                    # make y max the prev y
                    transformed_dataset.append([-np.inf, p[0], p[1], prev[1], -np.inf, p[2], p[-1], p[0], p[2]])
                else:
                    # overhang case, find all prev points with ...
                    transformed_dataset.append([-np.inf, p[0], p[1], prev[1], -np.inf, p[2], p[-1], p[0], p[2]])

            else:
                # create y max bound if under previous point (from z)
                if p[2] > prev[2]:
                    # make y max the prev y
                    transformed_dataset.append([-np.inf, p[0], p[1], prev[1], p[2], np.inf, p[-1], p[0], p[2]])
                else:
                    # overhang case, find all prev points with ...
                    transformed_dataset.append([-np.inf, p[0], p[1], prev[1], p[2], np.inf, p[-1], p[0], p[2]])
        
        return
    
    # def report_meo_to_boxes(self, A, isTypeLeft):
    #     # sort on 3rd dimension
    #     # A = [[3,3,1,0], [4,4,2,0], [2,2,3,0], [1,1,4,0], [4,0,5,0], [-1,4,6,0], [0,-1,7,0]]
    #     # A = [[4,4,1,0], [3,1,2,0], [0,3,3,0], [5,-1,4,0], [2,2,5,0], [1,1,6,0]]
    #     # A = [[4,4,1,0], [3,1,2,0], [1,3,3,0], [5,-1,4,0], [0,2,5,0]]
    #     A.sort(key=lambda p: p[2])
    
    #     meo_list = list()
    #     point_list = list()
    #     # find the max empty orthants of A using a plane sweep algorithm on d=3
    #     for it, point in enumerate(A):
    #         # empty case, add a single point as orthant
    #         if it == 0:
    #             # meo_list.append((point, [point, point, point]))
    #             point_list.append((point, [None, None, None]))
    #             # print("Initial point:", point_list[0][0])
    #             d_tree = DTree.DTree(meo_list)
    #             pd_tree = DTree.DTree(point_list)
    #         else:
    #             # print("\nStep: ", it)
    #             # print("Point:", point)
                
    #             # Q: old meo which need to be updated
    #             # QP: old point list which need to be updated
    #             # Q = d_tree.query_range_report([point[0], point[1]], [np.inf, np.inf])
    #             # QP = pd_tree.query_range_report([point[0], point[1]], [np.inf, np.inf])
    #             Q = d_tree.query_range_report([point[0], -np.inf], [np.inf, point[1]])
    #             QP = d_tree.query_range_report([point[0], -np.inf], [np.inf, point[1]])
                
    #             # print("QP:")
    #             if QP:
    #                 for qp in QP:
    #                     # print(qp.point + [qp.color])
    #                     pass
    #             # print("Q:")
                
    #             if Q:
    #                 for q in Q:
    #                     # print(q.point + [q.color])
    #                     pass
                
    #             if not QP:
    #                 # if pd_tree.query_range_report([-np.inf, -np.inf], [point[0], point[1]]) is None and not Q:
    #                 if pd_tree.query_range_report([-np.inf, point[1]], [point[0], np.inf]) is None:
    #                     # add orthants on ends of meo (diagnols)
    #                     point_list.sort(key=lambda p: p[0][0])
    #                     p1 = point_list[0][0]
    #                     p2 = point_list[-1][0]
    #                     if point[0] < p1[0]:
    #                         meo_list.append(([p1[0], point[1], point[2], point[3]], [p1, point, point]))
    #                         point_list.append((point, [None, None, None]))
    #                     elif point[0] > p2[0]:
    #                         meo_list.append(([point[0], p2[1], point[2], point[3]], [point, p2, point]))
    #                         point_list.append((point, [None, None, None]))
    #                     else:
    #                         # print("ERROR")        
    #                         pass
    #                 elif Q:
    #                     point_list.append((point, [None, None, None]))
    #                     for q in Q:
    #                         meo_list.append(([point[0], q.tup[1][1], point[2], point[3]], [point, q.tup[1], point]))
    #                         meo_list.append(([q.tup[0][0], point[1], point[2], point[3]], [q.tup[0], point, point]))
    #                 else:    
    #                     # print("not skyline; no updates on points/meo")
    #                     pass
    #             elif QP:
    #                 QP_list = list()
    #                 # print("QP =")
    #                 for qp in QP:
    #                     # print(qp.point + [qp.color])
    #                     QP_list.append(qp.point + [qp.color])
                        
    #                 point_list.append((point, [None, None, None]))
                    
    #                 if len(point_list) == 1:
    #                     # replace point with new point
    #                     # print("REMOVE POINT", point_list[0][0])
    #                     point_list.pop(0)
    #                 else:
    #                     # only if orthants are found
    #                     if Q:
    #                         for q in Q:
    #                             if q.tup[0] in QP_list and q.tup[1] in QP_list:
    #                                 continue
    #                             for qp in QP:
    #                                 if q.tup[0] == (qp.point + [qp.color]):
    #                                     meo_list.append(([point[0], q.point[1], point[2], point[3]], [point, (q.point + [q.color]), point]))
    #                                 elif q.tup[1] == (qp.point + [qp.color]):
    #                                     meo_list.append(([q.point[0], point[1], point[2], point[3]], [(q.point + [q.color]), point, point]))
                    
    #             if QP:
    #                 for q in QP:
    #                     for p in point_list:
    #                         (point, tup) = p
    #                         if point == (q.point + [q.color]):
    #                             # print("REMOVE POINT", q.point + [q.color])
    #                             point_list.remove(p)
    #                             break
                
    #             if Q:
    #                 for q in Q:
    #                     for p in meo_list:
    #                         (point, tup) = p
    #                         if point == (q.point + [q.color]):
    #                             # print("REMOVE MEO", q.point + [q.color])
    #                             meo_list.remove(p)
    #                             break
                            
    #             # print("New point list:")
    #             for p in point_list:
    #                 (point, tup) = p
    #                 # print(point)
    #             pd_tree = DTree.DTree(point_list)
                
    #             # print("New meo:")
    #             for p in meo_list:
    #                 (point, tup) = p
    #                 # print(point, tup)
    #             d_tree = DTree.DTree(meo_list)
                  
                
    #     transformed_dataset = list()
        
    #     point_list.sort(key=lambda p: p[0][0])
    #     p = point_list[0][0]
    #     # transformed_dataset.append([p[0], np.inf, p[1], np.inf, p[2], np.inf, p[-1], p[0], p[2]])
    #     if isTypeLeft:
    #         transformed_dataset.append([-np.inf, p[0], p[1], np.inf, -np.inf, p[2], p[-1], p[0], p[2]])
    #     else:
    #         transformed_dataset.append([-np.inf, p[0], p[1], np.inf, p[2], np.inf, p[-1], p[0], p[2]])
        
    #     for p in meo_list:
    #         s3 = max(p[1][0][2], p[1][1][2])
            
    #         # transformed_dataset.append([p[1][0][0], np.inf, p[1][0][1], p[1][1][1], s3, np.inf, p[-1], p[0][0], p[0][2]])
    #         if isTypeLeft:
    #             transformed_dataset.append([-np.inf, p[1][0][0], p[1][0][1], p[1][1][1], p[1][2][2], s3, p[1][0][-1], p[1][0][0], s3])
    #         else:
    #             transformed_dataset.append([-np.inf, p[1][0][0], p[1][0][1], p[1][1][1], s3, p[1][2][2], p[1][0][-1], p[1][0][0], s3])

    #     # print("boxes")   
    #     for t in transformed_dataset:
    #         print(t)
    #         pass
    #     print()
        
    #     # sys.exit()
    #     return transformed_dataset
    
    def report_meo_to_boxes(self, A, isTypeLeft):
        # print("starting boxes\n")
        
        # sort on 3rd dimension
        # A = [[10,10,1,0], [11,11,2,0], [12,8,3,0], [14,6,4,0], [11,9,5,0], [8,12,6,0], [9,7,7,0]]
        A.sort(key=lambda p: p[2])
        if isTypeLeft:
            A.reverse()
        
        complete_meo_list = list()
        meo_list = list()
        point_list = list()
        
        # inf_point = [np.inf, np.inf, np.inf, None]
        if isTypeLeft:
            inf_point = [-np.inf, np.inf, -np.inf]
        else:
            inf_point = [-np.inf, np.inf, +np.inf]
        
        # find the max empty orthants of A using a plane sweep algorithm on d=3
        for it, point in enumerate(A):
            
            # case 0, add a single point as orthant
            if it == 0:
                
                meo_list.append(([point[0], inf_point[1], inf_point[2]], [point, inf_point, inf_point])) 

                point_list.append((point, [None, None, None]))
                meo_tree = DTree.DTree(meo_list)
                point_tree = DTree.DTree(point_list)
            else:
                # print("\nStep: ", it)
                # print("Point:", point)
                # O: all orthants found from [new point, inf)
                # P: all points found from [new point, inf)
                
                # O = meo_tree.query_range_report([point[0], point[1]], [np.inf, np.inf])
                # P = point_tree.query_range_report([point[0], point[1]], [np.inf, np.inf])
                O = meo_tree.query_range_report([-np.inf, point[1]], [point[0], np.inf])
                P = point_tree.query_range_report([-np.inf, point[1]], [point[0], np.inf])
                
                # print("P found:")
                if P:
                    for p in P:
                        # print(p.point + [p.color])
                        pass
                # print("O found:")                
                if O:
                    for p in O:
                        # print(p.point + [p.color])
                        pass
                
                if not O:
                    # case 1, point is already in B(O), don't add point
                    # if point_tree.query_range_report([-np.inf, -np.inf], [point[0], point[1]]) is not None:
                    if point_tree.query_range_report([point[0], -np.inf], [np.inf, point[1]]) is not None:        
                        # print("CASE 1")
                        pass
                    
                    # case 2, point doesn't affect current O, add new point and orth under min box
                    else:
                        # print("CASE 2")
                        point_list.sort(key=lambda p: p[0][1]) # sort all points by y axis
                        
                        p1 = point_list[0][0] # first point in point_list has minimum y
                        # p1 = point_list[-1][0]

                        
                        meo_list.append(([point[0], p1[1], inf_point[2]],[point, p1, inf_point]))
                        point_list.append((point, [None, None, None]))
                
                elif O:
                    # print("CASE 3")
                    point_list.append((point, [None, None, None]))
                    try_meo = list()
                    for m in O:
                        [px,py,pz] = m.tup
                        [x,y] = m.point
                        z = pz[2]
                        complete_meo_list.append(([x,y,point[2]],[px,py,point]))
                        if P:
                            if not (m.tup[0] in P and m.tup[1] in P):  
                                try_meo.append(([point[0],y,z], [point,py,pz]))
                                try_meo.append(([x,point[1],z], [px,point,pz]))
                        elif not P:
                            try_meo.append(([point[0],y,z], [point,py,pz]))
                            try_meo.append(([x,point[1],z], [px,point,pz]))
                            
                    for m in try_meo:
                        ([x,y,z],[px,py,pz]) = m
                        # if (px[0] > py[0] or py[0] is np.inf) and px[1] < py[1]:
                        if (px[0] < py[0] or py[0] is -np.inf) and px[1] < py[1]:
                            meo_list.append(m)
                    
                if P:
                    for q in P:
                        for p in point_list:
                            (point, tup) = p
                            if point == (q.point + [q.color]):
                                # print("REMOVE POINT", q.point + [q.color])
                                point_list.remove(p)
                                break
                
                if O:
                    for q in O:
                        for p in meo_list:
                            (point, tup) = p
                            if point == (q.point + [q.color]):
                                # print("REMOVE MEO", q.point + [q.color])
                                meo_list.remove(p)
                                break
                            
                # print("New point list:")
                for p in point_list:
                    (point, tup) = p
                    # print(point)
                point_tree = DTree.DTree(point_list)
                
                # print("New meo:")
                for p in meo_list:
                    (point, tup) = p
                    # print(point, tup)
                meo_tree = DTree.DTree(meo_list)
                
                # print("Complete meo:")
                for p in complete_meo_list:
                    (point, tup) = p
                    # print(point, tup)
                meo_tree = DTree.DTree(meo_list)
                
        transformed_dataset = list()
        complete_meo_list += meo_list
        for m in complete_meo_list:
            ([x,y,z],[p1,p2,p3]) = m
            if p2 is inf_point and p3 is inf_point:
                # transformed_dataset.append([p1[0], np.inf, p1[1], np.inf, p1[2], np.inf, p1[-1], p1[0], p1[2]])
                if isTypeLeft:
                    transformed_dataset.append([-np.inf, p1[0], p1[1], np.inf, -np.inf, p1[2], p1[-1], p1[0], p1[2]])
                else:
                    transformed_dataset.append([-np.inf, p1[0], p1[1], np.inf, p1[2], np.inf, p1[-1], p1[0], p1[2]])
            else:
                if p2 is inf_point:
                    pmin = p1
                else:
                    pmin = min([p1,p2], key=lambda p: p[2])
                if p2 is inf_point:
                    pmax = p1
                else:
                    pmax = max([p1,p2], key=lambda p: p[2])
                    
                # transformed_dataset.append([p1[0], np.inf, p1[1], p2[1], pmax[2], p3[2], p1[-1], p1[0], pmax[2]])
                if isTypeLeft:
                    transformed_dataset.append([-np.inf, p1[0], p1[1], p2[1], p3[2], pmin[2], p1[-1], p1[0], pmax[2]])
                else:
                    transformed_dataset.append([-np.inf, p1[0], p1[1], p2[1], pmax[2], p3[2], p1[-1], p1[0], pmax[2]])

        print("boxes")   
        for t in transformed_dataset:
            print(t)
            pass
        print()
        
        # sys.exit()
        return transformed_dataset
    
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
                # matrix[i][j] = self.find_light_intersection(c_left, c_right)
                matrix[i][j] = 0
        
        return matrix
        
    def find_heavy_nodes(self, root, C=[]):
        if root is None:
            return 
        if root.left is None and root.right is None:
            return
        
        if root.count > self.x_const:
            C.append(root)
        
        self.find_heavy_nodes(root.left, C)
        self.find_heavy_nodes(root.right, C)
        
        return C
    
    def report_leaves(self, root, leaves=[]):
        if root is None:
            return
        if root.left is None and root.right is None:
            leaves.append(root.color)
            self.color_freqs[root.color - 1] += 1
        else: 
            self.report_leaves(root.left, leaves)
            self.report_leaves(root.right, leaves)
        return leaves
        
    
    def query_random_sample(self, min_point, max_point):
        split_node = self.report_split_node(self.root, min_point, max_point)
        
        # check if in y_range when split_node is leaf
        if split_node.left is None and split_node.right is None:
            if min_point[1] <= split_node.point[1] <= max_point[1]:
                return split_node
            else:
                return None
        
        # find canonical nodes from auxillary trees
        min_left = [-np.inf, min_point[0], -np.inf, max_point[0], -np.inf, min_point[1]]
        max_left = [min_point[0], np.inf, max_point[0], np.inf, min_point[1], np.inf]
        canonical_nodes_left = split_node.aux_left.report_colors(min_left, max_left)
        
        min_right = [-np.inf, min_point[0], -np.inf, max_point[0], -np.inf, max_point[1]]
        max_right = [min_point[0], np.inf, max_point[0], np.inf, max_point[1], np.inf]
        canonical_nodes_right = split_node.aux_right.report_colors(min_right, max_right)  
        
        left_count = 0
        right_count = 0
        for node in canonical_nodes_left:
            left_count += node.count
        for node in canonical_nodes_right:
            right_count += node.count
            
        # if left_count > 1 or right_count > 1:   
        #     print("count", left_count, right_count)
        # if left_count > self.num_colors:
        for node in canonical_nodes_left:
            leaves = self.report_leaves(node)
                # for l in leaves:
                #     print(l)
        # if right_count > self.num_colors:
        for node in canonical_nodes_right:
            leaves = self.report_leaves(node)
                # for l in leaves:
                #     print(l)
        
        num_counts = 0
        sum_counts = 0
        for node in canonical_nodes_left:
            node.search_weight = node.weight
            num_counts += 1
            sum_counts += node.count
        for node in canonical_nodes_right:
            node.search_weight = node.weight
            num_counts += 1
            sum_counts += node.count
        
        self.num_counts += num_counts
        self.sum_counts += sum_counts
        if self.num_counts != 0:
            self.avg_count = self.sum_counts / self.num_counts
        
        if not canonical_nodes_left and not canonical_nodes_right:
            return None
        
        self.light_count = 0
        self.heavy_count = 0
        
        # find and remove intersection between every pairing of canonical nodes
        for node_left in canonical_nodes_left:
            for node_right in canonical_nodes_right:
                node_right.search_weight -= self.report_intersection(node_left, node_right, split_node)
                if node_right.search_weight < 0:
                    node_right.search_weight = 0
        
        canonical_nodes = list()
        if canonical_nodes_left:
            canonical_nodes += canonical_nodes_left         
        if canonical_nodes_right:
            canonical_nodes += canonical_nodes_right   
        
        # randomly select a canonical node
        max_node = canonical_nodes[0]
        if max_node.weight != 0:
            max_key = np.random.random() ** (1 / max_node.weight)
        else:
            max_key = 0
        for node in canonical_nodes:
            if node.weight != 0:
                key = np.random.random() ** (1 / node.weight)
            else:
                key = 0
            if key > max_key:
                max_node = node
                max_key = key
                
        # randomly walk down canonical node and return leaf node
        v = max_node
        while v.left is not None and v.right is not None:
            if np.random.random() ** (1 / v.left.weight) > np.random.random() ** (1 / v.right.weight):
                v = v.left
            else:
                v = v.right
        return v
        
    def report_intersection(self, node_left, node_right, split_node):
        if node_left.count > self.x_const and node_right.count > self.x_const:
            weight = self.find_heavy_intersection(node_left, node_right, split_node)
            self.heavy_count += 1
        else:
            weight = self.find_light_intersection(node_left, node_right)
            self.light_count += 1
        return weight
    
    def find_heavy_intersection(self, c_left, c_right, split_node):
        return 0
        print(c_left.node_id, c_right.node_id)
        print(split_node.left_to_idx.keys())
        left_idx = split_node.left_to_idx[c_left.node_id]
        right_idx = split_node.right_to_idx[c_right.node_id]
        return split_node.matrix[left_idx][right_idx]
    
    found_color_intersection = None
    intersection_weight = None
    def find_light_intersection(self, c_left, c_right):
        if c_left is None:
            return 0
        
        # when at leaf, remove leaf's color from subtree at c_right
        if c_left.left is None and c_left.right is None:
            self.found_color_intersection = False
            self.intersection_weight = 0
            self.find_light_intersection_helper(c_left.color, c_right, c_right)
        
        self.find_light_intersection(c_left.left, c_right)
        self.find_light_intersection(c_left.right, c_right)
        
        return self.intersection_weight
    
    def find_light_intersection_helper(self, color, c_right, root):
        if root is None or self.found_color_intersection is True:
            return
        
        # when at leaf, subtract c_right's weight by weight of searched color
        if root.left is None and root.right is None and (root.color == color):
            self.intersection_weight += self.color_weights[color]
            self.found_color_intersection = True
            
        self.find_light_intersection_helper(color, c_right, root.left)
        self.find_light_intersection_helper(color, c_right, root.right)
    
    # split node on y-coordinates (axis=1)
    def report_split_node(self, root, min_point, max_point):
        axis = 1
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