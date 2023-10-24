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

# class used to contain one dimensional points in range tree
class Node():
    def __init__(self, x_val, color):
        self.x_val = x_val
        self.color = color
    left = None
    right = None
    key = None
    maxNode = None

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
# D: dictionary of colors and weights
def buildRangeTree(P, D):
    # base case, P has one node
    # create leaf node, v with value of node
    # set v's key using v's color, and set v's maxNode to itself
    if len(P) <= 1:
        v = Node(P[0].x_val, P[0].color)
        v.key = np.random.random() ** (1 / D[v.color])
        v.maxNode = v
        
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

# returns the node with the greatest key stored within the canonical node
# C: set of all canonical nodes
def weightedRandomColorNode(C):
    # return if C is empty
    if not C:
        print('No Nodes found in range')
        return None
    
    # initialize c_max as first element in list
    c_max = C[0]
    
    # assign c_max to c with the greatest key
    for c in  C:
        if c.key > c_max.key:
            c_max = c
            
    # return the node stored at c_max's maxNode 
    return c_max.maxNode
    
# ----------------------------------------------------------------------------------------------------------------
# example usage of uniform random sampling

# create a list of nodes to use as database
database = list()
databaseSize = 1000
colorDict = {'red': 1, 'blue': 3, 'yellow': 6}
for i in range(databaseSize):
    random = np.random.randint(0, 3)
    if random == 0:
        database.append(Node(i, 'red'))
    elif random == 1:
        database.append(Node(i, 'blue'))
    else: 
        database.append(Node(i, 'yellow'))
            
# build the range tree and list of canonical nodes for a given query range 
rangeTree = buildRangeTree(database, colorDict)
queryRange = QueryRange(200, 300)
canonicalNodes = findCanonicalSet(rangeTree, queryRange)

# query for a random node in database between the given query range
randomNode = weightedRandomColorNode(canonicalNodes)
print('Random node:', randomNode.x_val, randomNode.color, '\n')

# ----------------------------------------------------------------------------------------------------------------
# test below proves weightedRandomColorNode has a distribution proportional to the weights of colors

freqList = list()
numIterations = 500

for i in range(len(colorDict)):
    freqList.append(0)
    
for i in range(numIterations):
    # rebuild the tree and query on that tree
    rangeTree = buildRangeTree(database, colorDict)
    canonicalNodes = findCanonicalSet(rangeTree, queryRange)
    randomNode = weightedRandomColorNode(canonicalNodes)
    
    if randomNode.color == 'red':
        freqList[0] = freqList[0] + 1
    if randomNode.color == 'blue':
        freqList[1] = freqList[1] + 1
    if randomNode.color == 'yellow':
        freqList[2] = freqList[2] + 1

print('Frequencies of colors (actual - theoretical):')
print('red    %:', freqList[0] / numIterations, '-', 1/10)
print('blue   %:', freqList[1] / numIterations, '-', 3/10)
print('yellow %:', freqList[2] / numIterations, '-', 6/10)

freqTable = {}
x_min = None

for i in range(numIterations):
    # rebuild the tree and query on that tree
    rangeTree = buildRangeTree(database, colorDict)
    canonicalNodes = findCanonicalSet(rangeTree, queryRange)
    randomNode = weightedRandomColorNode(canonicalNodes)
    
    if randomNode is None:
        continue
    if x_min is None:
        x_min = randomNode.x_val
        x_max = x_min
    if (randomNode.x_val < x_min):
        x_min = randomNode.x_val
    if (randomNode.x_val > x_max):
        x_max = randomNode.x_val

print('\nRange of random nodes (actual - theoretical):')
print('[' + str(x_min) + ',' + str(x_max) + '] - [' + str(queryRange.x_min) + ',' + str(queryRange.x_max) + ']')

