# -*- coding: utf-8 -*-
"""
Created on: October 4, 2023
Authors: Nathaniel Madrigal, Alexander Madrigal

"""

import numpy as np

# class used to contain one dimensional points in range tree
class Node():
    def __init__(self, x_val):
        self.x_val = x_val
    left = None
    right = None
    weight = None

# class defines the search interval of a query
class QueryRange():
    def __init__(self, x_min, x_max):
        self.x_min = x_min
        self.x_max = x_max
        
# key for sorting list of nodes on their x_val
# ex. P.sort(key=getX)
def getX(p):
    return p.x_val

# returns the root node of a built 1-D range tree
# P: list of nodes
def buildRangeTree(P):
    # base case, P has one node
    # create leaf node v with value of node and weight of 1
    if len(P) <= 1:
        v = Node(P[0].x_val)
        v.weight = 1
    
    # recursive case, P has more than one node
    else:
        # sort the list and split into two sublists by median node
        P.sort(key=getX)
        if len(P) % 2 == 0:
            mid = (len(P) // 2) - 1
        else:
            mid = len(P) // 2
        P_left = P[:mid + 1]
        P_right = P[mid + 1:]
        
        # create an internal node v with the value of the median node
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

# return a list of all canonical nodes
# root: root node of 1-D range tree
# Q: query range
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

# returns a uniform random node from the set of all canonical nodes 
# C: set of all canonical nodes
def uniformRandomNode(C):
    # return if C is empty
    if not C:
        print('No Nodes found in range')
        return None
    
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

# ----------------------------------------------------------------------------------------------------------------
# example usage of uniform random sampling

# create a list of nodes to use as database
database = list()
databaseSize = 1000
for i in range(databaseSize):
    database.append(Node(i))

# build the range tree and list of canonical nodes for a given query range 
rangeTree = buildRangeTree(database)
queryRange = QueryRange(450, 465)
canonicalNodes = findCanonicalSet(rangeTree, queryRange)

# query for a random node in database between the given query range
randomNode = uniformRandomNode(canonicalNodes)

print('Query result:', randomNode.x_val, '\n')

# ----------------------------------------------------------------------------------------------------------------
# test below proves code correctness

freqTable = {}
numIterations = 1000
x_min = None

for i in range(numIterations):
    randomNode = uniformRandomNode(canonicalNodes)
    if randomNode is None:
        continue
    if x_min is None:
        x_min = randomNode.x_val
        x_max = x_min
    if (randomNode.x_val < x_min):
        x_min = randomNode.x_val
    if (randomNode.x_val > x_max):
        x_max = randomNode.x_val
    key = "("+str(randomNode.x_val)+")"
    if key in freqTable.keys():
        freqTable[key] = freqTable[key] + 1 
    else:
        freqTable[key] = 1

print('Frequencies of random nodes:')
for x in freqTable:
    val = freqTable[x]
    while len(x) < 10:
        x = x + " "
    print(x, "%:", val / numIterations)

print('\nRange of random nodes:')
print('[' + str(x_min) + ',' + str(x_max) + ']')