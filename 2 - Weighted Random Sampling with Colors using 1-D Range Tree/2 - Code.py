# -*- coding: utf-8 -*-
"""
Created on: October 12, 2023
Authors: Alexander Madrigal, Nathaniel Madrigal
    
Problem: Build a 1-D range tree that randomly samples a leaf node according to the probability of its 
         weighted color dependent on a query range (the same query range will always return the same leaf node)
         
Procedure:
    1 - Within the range tree, store within each parent node the child node with the greatest key 
    2 - Find the set of all canonical nodes within the query range
    3 - Select the canonical node with the greatest key

Background:
    1. A key is a random number dependent on its weight such that returning the greatest key returns a random key 
       with probabilities associated with its weight
"""

import numpy as np

class Node():
    def __init__(self, x_val, color):
        self.x_val = x_val
        self.color = color
        
    left = None
    right = None
    key = None
    maxNode = None

class QueryRange():
    def __init__(self, x_min, x_max):
        self.x_min = x_min
        self.x_max = x_max
        
# key for sorting list of nodes on their x_val
def getX(p):
    return p.x_val

# returns the root node of a built 1-D range tree
# P: list of points
# D: dictionary of colors and weights
def buildRangeTree(P, D):
    # base case, P has one point
    # create leaf node, v with value of point
    # set v's key using v's color, and set v's maxNode to itself
    if len(P) <= 1:
        v = Node(P[0].x_val, P[0].color)
        v.key = np.random.random() ** (1 / D[v.color])
        v.maxNode = v
        
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
        v = Node(P[mid].x_val, P[mid].color)
        v.left = buildRangeTree(P_left, D)
        v.right = buildRangeTree(P_right, D)
        
        # assign v's key to the greatest key between v's left & right
        # assign v's maxNode to the child node with the greater key
        if v.left.key > v.right.key:
            v.key = v.left.key
            v.maxNode = v.left.maxNode
        else:
            v.key = v.right.key
            v.maxNode = v.right.maxNode
            
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

# returns a list of the set of all canonical nodes
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
        # follow path to x_min from split node
        v = sp.left
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
        v = sp.right
        while v.left is not None and v.right is not None:
            if v.x_val <= Q.x_max:
                C.append(v.left)
                v = v.right
            else:
                v = v.left
        if v.x_val >= Q.x_min and v.x_val <= Q.x_max:
            C.append(v)
    
    return C

# find the canonical node with the greatest key
# returns the node with the greatest key stored within the canonical node
# C: set of all canonical nodes
def weightedRandomColorNode(C):
    # return if C is empty
    if not C:
        return
    
    # initialize c_max as first element in list
    c_max = C[0]
    
    # assign c_max to c with the greatest key
    for c in  C:
        if c.key > c_max.key:
            c_max = c
            
    # return the node stored at c_max's maxNode 
    return c_max.maxNode
    
# returns the frequency of all nodes within the query range
def proveUniformRandom(P, Q, D, numIterations):
    freq_list = list()
    
    for i in range(Q.x_max - Q.x_min + 1):
        freq_list.append(0)
    
    for i in range(numIterations):
        range_tree = buildRangeTree(P, D)
        canonical_set = findCanonicalSet(range_tree, Q)
        random_node = weightedRandomColorNode(canonical_set)
        freq_list[random_node.x_val - Q.x_min] = freq_list[random_node.x_val - Q.x_min] + 1
    
    for i in range(len(freq_list)):
        print('element', i + Q.x_min, '%', freq_list[i] / numIterations)
    
# returns the frequency of all colors within query range
def proveWeightedColors(P, Q, D, numIterations):
    for i in range(len(D)):
        freq_list.append(0)
        
    for i in range(numIterations):
        range_tree = buildRangeTree(P, D)
        canonical_set = findCanonicalSet(range_tree, Q)
        
        random_node = weightedRandomColorNode(canonical_set)
        
        if random_node.color == 'red':
            freq_list[0] = freq_list[0] + 1
        if random_node.color == 'blue':
            freq_list[1] = freq_list[1] + 1
        if random_node.color == 'yellow':
            freq_list[2] = freq_list[2] + 1

    print('red %:', freq_list[0] / numIterations)
    print('blue %:', freq_list[1] / numIterations)
    print('yellow %:', freq_list[2] / numIterations)
    
# ----------------------------------------------------------------------------------------------------------------
# example usage of uniform random sampling

# database is a list containing values 0 to 999
database = list()
database_size = 1000
colorDict = {'red': 1, 'blue': 3, 'yellow': 6}
for i in range(database_size):
    random = np.random.randint(0, 3)
    if random == 0:
        database.append(Node(i, 'red'))
    elif random == 1:
        database.append(Node(i, 'blue'))
    else: 
        database.append(Node(i, 'yellow'))
            
# find weighted colored node in database between the query range
freq_list = list()
numIterations = 1000
query_range = QueryRange(200, 300)

range_tree = buildRangeTree(database, colorDict)
canonical_set = findCanonicalSet(range_tree, query_range)
random_node = weightedRandomColorNode(canonical_set)
print(random_node.x_val, random_node.color)
print()

# proveUniformRandom(database, query_range, colorDict, numIterations)
# print()
#proveWeightedColors(database, query_range, colorDict, numIterations)


