# -*- coding: utf-8 -*-
"""
Created on: October 18, 2023
Authors: Nathaniel Madrigal, Alexander Madrigal

Objective:
    1. Implement scalable multidimensional range tree
    2. Remedy restriction of non-repeating coordinates in range tree
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
    
    # less-than function; used to sort Nodes in sortNodes function
    # allows for distinct points with same coordinates in any dimension
    def le(self, other, d):
        if self.getVal(d) < other.getVal(d):
            return True
        elif self.getVal(d) > other.getVal(d):
            return False
        # if values on d are equal, compare on other dimensions
        else:
            for i in range(1, MAX_DIMENSION + 1):
                if i != d:
                    if self.getVal(i) < other.getVal(i):
                        return True
                    elif self.getVal(i) > other.getVal(i):
                        return False
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
            if not arrNode[i].le(pivot, d):
                break
        while True:
            j = j - 1
            if not pivot.le(arrNode[j], d):
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
# P: list of points
# d: starting dimension, always starts at one
def buildRangeTree(P, d):
    if not P:
        raise Exception('List of Nodes is empty')
    
    if d > MAX_DIMENSION:
        return None
    
    # build an associated tree with the same set of points in the d+1 dimension
    T_assoc = buildRangeTree(P, d + 1)
    
    # base case, P has one point
    # create leaf node, v with value of point and weight of 1
    if len(P) == 1:
        v = Node(P[0].arrValues)
        v.weight = 1
    
    # recursive case, P has more than one point
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
def findCanonicalSet(root, Q, d):    
    if root is None:
        return
    
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
    
    if d == MAX_DIMENSION:
        return C
    else:
        if not C:
            return C
        c_sum = findCanonicalSet(C[0].T_assoc, Q, d + 1)
        for i in range(1, len(C)):
            if not c_sum:
                c_sum = findCanonicalSet(C[i].T_assoc, Q, d + 1)
            else:
                c_assoc = findCanonicalSet(C[i].T_assoc, Q, d + 1)
                if c_assoc:
                    c_sum = c_sum + c_assoc
        return c_sum

# returns a uniform random node from the set of all canonical nodes 
# C: set of all canonical nodes
def uniformRandomNode(C):
    # concept: returning the node with greatest key is equal to returning a weighted random node
    
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

def printLeaves(root):
    if root.left is None and root.right is None:
        print(root.getVal(1), root.getVal(2), root.getVal(3))
    else:
        printLeaves(root.left)
        printLeaves(root.right)
    

# prints the frequency of all nodes within the query range
# prints the range of values inside query results
def proveUniformRandom(C, numIterations):
    freqTable = {}
    x_min = None
    x_max = None
    y_min = None
    y_max = None
    z_min = None
    z_max = None
    
    for i in range(numIterations):
        randomNode = uniformRandomNode(C)
        if randomNode is None:
            continue
        if x_min is None:
            x_min = randomNode.getVal(1)
            x_max = randomNode.getVal(1)
            y_min = randomNode.getVal(2)
            y_max = randomNode.getVal(2)
            z_min = randomNode.getVal(3)
            z_max = randomNode.getVal(3)
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
    
    for x in freqTable:
        val = freqTable[x]
        while len(x) < 20:
            x = x + " "
        print(x, "%:", val / numIterations)
        
    print('x: [' + str(x_min) + ',' + str(x_max) + ']')
    print('y: [' + str(y_min) + ',' + str(y_max) + ']')
    print('z: [' + str(z_min) + ',' + str(z_max) + ']')

# ----------------------------------------------------------------------------------------------------------------
# example usage of uniform random sampling

# build a random set of points for a database
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
    
# build the range tree
rangeTree = buildRangeTree(database, 1)
x_range = Range(500, 1000)
y_range = Range(100, 600)
z_range = Range(750, 850)
queryRange = QueryRange([x_range, y_range, z_range])
canonicalNodes = findCanonicalSet(rangeTree, queryRange, 1)

# query for a singular node
randomNode = uniformRandomNode(canonicalNodes)
if randomNode != None:
     print('query result:', randomNode.getVal(1), randomNode.getVal(2), randomNode.getVal(3))

# ----------------------------------------------------------------------------------------------------------------
# commented code below proves that:
#     1. nodes are returned uniformly at random
#     2. nodes are within query range

# numIterations = 1000
# proveUniformRandom(canonicalNodes, numIterations)
