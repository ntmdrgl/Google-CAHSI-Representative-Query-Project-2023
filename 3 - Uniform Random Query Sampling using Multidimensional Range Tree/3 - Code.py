# -*- coding: utf-8 -*-
"""
Created on: October 18, 2023
Authors: Nathaniel Madrigal, Alexander Madrigal

Objective:
    1. Implement scalable multidimensional range tree
    2. Sample a node within an axis-aligned query range uniformly at random
"""

import numpy as np

MAX_DIMENSION = 3

class Node():
    def __init__(self, arrValues):
        # each Node will contain a direct-address table of values with dimension as key  
        self.arrValues = list(arrValues)
        
        if len(self.arrValues) != MAX_DIMENSION:
            raise Exception('Incorrect number of values given in Node')
            
    # look-up value at dimension d
    def getVal(self, d):
        return self.arrValues[d - 1]
    
    left = None
    right = None
    weight = None
    T_assoc = None

# class for 1-dimensional range
class Range():
    def __init__(self, min, max):
        self.min = min
        self.max = max

# class containing an array of Ranges
class QueryRange():
    def __init__(self, arrRanges):
        # direct-address table of ranges with dimension as key
        self.arrRanges = arrRanges
    
        if len(self.arrRanges) != MAX_DIMENSION:
            raise Exception('Incorrect number of Ranges given in QueryRange')
    
    # look-up range at dimension d
    def getRange(self, d):
        return self.arrRanges[d - 1]

# helper function for sortNodes function
def partition(arrNode, low, high, d):
    pivot = arrNode[(low + high) // 2]
    i = low - 1
    j = high + 1
    while True:
        while True:
            i = i + 1
            if arrNode[i].getVal(d) >= pivot.getVal(d):
                break
        while True:
            j = j - 1
            if arrNode[j].getVal(d) <= pivot.getVal(d):
                break
        if i < j:
            (arrNode[i], arrNode[j]) = (arrNode[j], arrNode[i])
        else:
            return j

# sort list of Nodes at certain dimension using quicksort
def sortNodes(arrNode, low, high, d):
    if low < high:
        pi = partition(arrNode, low, high, d)
        sortNodes(arrNode, low, pi, d)
        sortNodes(arrNode, pi + 1, high, d)

# returns the root node of a built multidimensional range tree
# P: list of nodes
# d: starting dimension, always starts at one
def buildRangeTree(P, d):
    if d > MAX_DIMENSION:
        return None
    
    # build an associated tree with the same set of nodes in the d+1 dimension
    T_assoc = buildRangeTree(P, d + 1)
    
    # base case, P has one point
    # create leaf node, v with value of point and weight of 1
    if len(P) == 1:
        v = Node(P[0].arrValues)
        v.weight = 1
    
    # recursive case, P has more than one node
    else:
        # sort the list and split into two sublists by median node
        sortNodes(P, 0, len(P) - 1, d)
        if len(P) % 2 == 0:
            mid = (len(P) // 2) - 1
        else:
            mid = len(P) // 2
        P_left = P[:mid + 1]
        P_right = P[mid + 1:]
        
        # create an internal node, v with the value of the median node
        # recursively call buildRangeTree on P's left & right sublists to assign v's left & right children 
        # assign weight of internal node as sum of children's weights
        # assign T_assoc as v's associate tree
        v = Node(P[mid].arrValues)
        v.left = buildRangeTree(P_left, d)
        v.right = buildRangeTree(P_right, d)
        v.weight = v.left.weight + v.right.weight
        v.T_assoc = T_assoc
        
    return v
    
# returns a node inside the query range which splits to all subleafs in query range
# root: root node of 1-D range tree
# Q: query range
# d: dimension
def findSplitNode(root, Q, d):
    v = root
    # loop until node v is at a leaf or is inside the query range
    while (v.left is not None and v.right is not None and (v.getVal(d) >= Q.getRange(d).max or v.getVal(d) < Q.getRange(d).min)):
        if v.getVal(d) >= Q.getRange(d).max:
            v = v.left
        else:
            v = v.right
    return v

# return a list of the set of all canonical nodes
# root: root node of 1-D range tree
# Q: query range
# d: starting dimension, always starts at one
def findCanonicalSet(root, Q, d):    
    # start search from the split node, sp and add valid canonical nodes to the set of all canonical nodes, C
    C = list()
    sp = findSplitNode(root, Q, d)
    # if sp is leaf
    if sp.left is None and sp.right is None:
        # check if in query range
        if sp.getVal(d) >= Q.getRange(d).min and sp.getVal(d) <= Q.getRange(d).max:
            C.append(sp)
    
    # if sp is internal node
    else:
        # follow path to minimum value in range from split node
        v = sp.left
        # loop while v is not at leaf
        while v.left is not None and v.right is not None:
            # if v is above minimum boundary, add v's right to C
            if v.getVal(d) >= Q.getRange(d).min:
                C.append(v.right)
                v = v.left
            else:
                v = v.right
        # check if the leaf node v traversed into is in range
        if v.getVal(d) >= Q.getRange(d).min and v.getVal(d) <= Q.getRange(d).max:
            C.append(v)
            
        # same process as following path to minimum value but now following path to maximum value in range
        v = sp.right
        while v.left is not None and v.right is not None:
            if v.getVal(d) <= Q.getRange(d).max:
                C.append(v.left)
                v = v.right
            else:
                v = v.left
        if v.getVal(d) >= Q.getRange(d).min and v.getVal(d) <= Q.getRange(d).max:
            C.append(v)
    
    # base case, return list of canonical nodes if at highest dimension or list is empty
    if d == MAX_DIMENSION or (not C):
        return C
    else:
        # recursive case, create and return a list of all canonical nodes in associate trees
        C_sum = list()
        
        # loop through every canonical node in C
        for i in range(len(C)):
            # don't recursively call if canonical node has an empty T_assoc
            if C[i].T_assoc is None:
                continue
            # create a list of canonical nodes for T_assoc
            C_assoc = findCanonicalSet(C[i].T_assoc, Q, d + 1)
            # add to C_sum only if C_assoc contains an node
            if C_assoc:
                C_sum = C_sum + C_assoc
        return C_sum

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

maxCoordinateValue = 1000
x_coord = list()
y_coord = list()
z_coord = list()

for i in range(maxCoordinateValue):
    x_coord.append(i)
    y_coord.append(i)
    z_coord.append(i)

databaseSize = 1000
for i in range(databaseSize):
    x = x_coord.pop(np.random.randint(0, len(x_coord)))
    y = y_coord.pop(np.random.randint(0, len(y_coord)))
    z = z_coord.pop(np.random.randint(0, len(z_coord)))
    database.append( Node([x, y, z]) )
    
# build the range tree and list of canonical nodes for a given query range 
rangeTree = buildRangeTree(database, 1)
x_range = Range(500, 1000)
y_range = Range(400, 600)
z_range = Range(750, 850)
queryRange = QueryRange([x_range, y_range, z_range])
canonicalNodes = findCanonicalSet(rangeTree, queryRange, 1)

# query for a random node in database between the given query range
randomNode = uniformRandomNode(canonicalNodes)
if randomNode != None:
     print('Random node:', randomNode.getVal(1), randomNode.getVal(2), randomNode.getVal(3), '\n')

# ----------------------------------------------------------------------------------------------------------------
# test below proves code correctness

freqTable = {}
numIterations = 2000
x_min = None

for i in range(numIterations):
    randomNode = uniformRandomNode(canonicalNodes)
    if randomNode is None:
        continue
    if x_min is None:
        x_min = randomNode.getVal(1)
        x_max = x_min
        y_min = randomNode.getVal(2)
        y_max = y_min
        z_min = randomNode.getVal(3)
        z_max = z_min
    if (randomNode.getVal(1) < x_min):
        x_min = randomNode.getVal(1)
    if (randomNode.getVal(1) > x_max):
        x_max = randomNode.getVal(1)
    if (randomNode.getVal(2) < y_min):
        y_min = randomNode.getVal(2)
    if (randomNode.getVal(2) > y_max):
        y_max = randomNode.getVal(2)
    if (randomNode.getVal(3) < z_min):
        z_min = randomNode.getVal(3)
    if (randomNode.getVal(3) > y_max):
        z_max = randomNode.getVal(3)   
    key = "("+str(randomNode.getVal(1))+","+str(randomNode.getVal(2))+","+str(randomNode.getVal(3))+")"
    if key in freqTable.keys():
        freqTable[key] = freqTable[key] + 1 
    else:
        freqTable[key] = 1

print('Frequencies of random nodes:')
for x in freqTable:
    val = freqTable[x]
    while len(x) < 17:
        x = x + " "
    print(x, "%:", val / numIterations)
    
print('\nRange of random nodes (actual - theoretical):')
print('x: [' + str(x_min) + ',' + str(x_max) + '] - [' + str(x_range.min) + ',' + str(x_range.max) + ']')
print('y: [' + str(y_min) + ',' + str(y_max) + '] - [' + str(y_range.min) + ',' + str(y_range.max) + ']')
print('z: [' + str(z_min) + ',' + str(z_max) + '] - [' + str(z_range.min) + ',' + str(z_range.max) + ']')
