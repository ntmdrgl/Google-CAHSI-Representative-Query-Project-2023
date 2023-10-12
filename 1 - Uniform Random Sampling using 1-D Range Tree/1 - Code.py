# -*- coding: utf-8 -*-
"""
Created on: October 4, 2023
Authors: Nathaniel Madrigal, Alexander Madrigal

Problem: Given a query in a 1-D range tree, randomly sample a leaf node uniformly

Procedure:
    1 - Associate every internal node in the range tree with a weight equal to the number of leaves
    2 - Find the set of all canonical nodes that defines a query range
    3 - Randomly select a canonical node from a set of all canonical nodes with probablities associated with each canonical node's weight
    4 - Randomly select a leaf from chosen canonical node with probablities associated with each node's weight
"""

import numpy as np

class Node():
    def __init__(self, x_val):
        self.x_val = x_val
        
    def setObjects(self, left, right, weight):
        self.left = left
        self.right = right
        self.weight = weight
        
    left = None
    right = None
    weight = None

class QueryRange():
    def __init__(self, x_min, x_max):
        self.x_min = x_min
        self.x_max = x_max
        
# key for sorting list of nodes on their x_val
def getX(p):
    return p.x_val

# returns the root node of a built 1-D range tree
# P: list of points
def buildRangeTree(P):
    # base case, P has one point
    # create leaf node, v with value of point and weight of 1
    if len(P) <= 1:
        v = Node(P[0].x_val)
        v.weight = 1
    
    # recursive case, P has more than one point
    else:
        # sort the list and split into two sublists by median node
        P.sort(key=getX)
        if len(P) % 2 == 0:
            mid = (len(P) // 2) - 1
        else:
            mid = len(P) // 2
        P_left = P[:mid + 1]
        P_right = P[mid + 1:]
        
        # create an internal node, v with the value of the median node
        # recursively call buildRangeTree on P's left & right sublists to assign v's left & right children 
        # assign weight of internal node as sum of children's weights
        v = Node(P[mid].x_val)
        v.left = buildRangeTree(P_left)
        v.right = buildRangeTree(P_right)
        v.weight = v.left.weight + v.right.weight
        
    return v
    
# returns a node inside the query range which splits to all subleafs in query range
# root: root node of 1-D range tree
# Q: query range
def findSplitNode(root, Q):
    v = root
    # loop until node v is at a leaf or is inside the query range
    while (v.left is not None and v.right is not None and (v.x_val >= Q.x_max or v.x_val < Q.x_min)):
        if v.x_val >= Q.x_max:
            v = v.left
        else:
            v = v.right
    return v

# return a list of the set of all canonical nodes
def findCanonicalSet(root, Q):
    # start search from the split node, sp and add valid canonical nodes to the set of all canonical nodes, C
    C = list()
    sp = findSplitNode(root, Q)
   
    # if sp is leaf
    if sp.left is None and sp.right is None:
        # check if in query range
        if sp.x_val >= Q.x_min and sp.x_val <= Q.x_max:
            C.append(sp)
    
    # if sp is internal node
    else:
        # follow path to x_min
        # create node, v to search left sub tree of sp
        v = Node(sp.left.x_val)
        v.setObjects(sp.left.left, sp.left.right, sp.left.weight)
        
        # loop while v is not at leaf
        while v.left is not None and v.right is not None:
            # if v is above minimum boundary, add v's right to C
            if v.x_val >= Q.x_min:
                C.append(v.right)
                v = v.left
            else:
                v = v.right
        # check if the leaf node v traversed into is in range
        if v.x_val >= Q.x_min and v.x_val <= Q.x_max:
            C.append(v)
            
        # same process as following path to x_min but now following path to x_max
        v = Node(sp.right.x_val)
        v.setObjects(sp.right.left, sp.right.right, sp.right.weight)
        while v.left is not None and v.right is not None:
            if v.x_val <= Q.x_max:
                C.append(v.left)
                v = v.right
            else:
                v = v.left
        if v.x_val >= Q.x_min and v.x_val <= Q.x_max:
            C.append(v)
    
    return C

# returns a uniform random node from the set of all canonical nodes 
# C: set of all canonical nodes
def uniformRandomNode(C):
    # concept: returning the node with greatest key is equal to returning a weighted random node
    
    # c_max: canonical node with greatest key
    # initialize c_max as the first index of C
    c_max = C[0]
    c_max_key = np.random.random() ** (1 / c_max.weight)
    
    # loop from second node to end of C
    # find the canonical node with the greatest key in C and assign to c_max
    for i in range(1, len(C)):
        c = C[i]
        c_key = np.random.random() ** (1 / c.weight)
        # replace c_max if the current canonical node has a greater key
        if c_key > c_max_key:
            c_max = c
            c_max_key = c_key
    
    # traverse down and select a leaf node from c_max
    v = c_max
    # loop until node v is a leaf
    while v.left is not None and v.right is not None:
        # compare keys of left and right children
        # traverse path with greatest key
        if (np.random.random() ** (1 / v.left.weight) >= np.random.random() ** (1 / v.right.weight)):
            v = v.left
        else:
            v = v.right
    
    # return leaf node from c_max
    return v

def proveUniformRandom(C, Q, numIterations):
    freq_list = list()
    for i in range(Q.x_max - Q.x_min + 1):
        freq_list.append(0)
    
    for i in range(numIterations):
        random_node = uniformRandomNode(C)
        freq_list[random_node.x_val - Q.x_min] = freq_list[random_node.x_val - Q.x_min] + 1
        
    for i in range(len(freq_list)):
        print("element", i + Q.x_min, "%:", freq_list[i] / numIterations)

# ----------------------------------------------------------------------------------------------------------------
# example usage of uniform random sampling

# database is a list containing values 0 to 999
database = list()
database_size = 1000
for i in range(database_size):
    database.append(Node(i))

# find random node in database between the query range 20 to 30
range_tree = buildRangeTree(database)
query_range = QueryRange(20, 30)
canonical_set = findCanonicalSet(range_tree, query_range)
random_node = uniformRandomNode(canonical_set)

print(random_node.x_val)
# print()
# proveUniformRandom(canonical_set, query_range, 1000)