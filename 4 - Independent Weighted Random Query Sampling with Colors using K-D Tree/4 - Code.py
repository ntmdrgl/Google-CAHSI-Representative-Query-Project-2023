# -*- coding: utf-8 -*-
"""
Created on: October 23, 2023
Authors: Alexander Madrigal, Nathaniel Madrigal
         
Objective: Randomly sample points with weight colors using a query. Have all randomly selected points be independent of query 
           (if the query does not change, the points will still be randomly selected)

Procedure:
    1 - For all colors, create a sorted list in increasing order and a 1-D range tree
    2 - For all point in all colored lists, insert (point, predecessor of point) in a 2-D list
    3 - Build a K-D tree using the 2-D list of points
    4 - Make a list of points using the query range [x_min, x_max] x (-infinity, x_min)
    5 - Since every point has a different color, randomly select a point with probabilies based 
        on weight of the point's color
    6 - Using the color of the selected point, find a uniform random node on the range tree 
        associated with that color 
"""



import numpy as np
import math

class BoundingBox():
    def __init__(self, x_min, x_max, y_min = None, y_max = None):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        
class Node():
    def __init__(self, color, x_val, y_val = None):
        self.x_val = x_val
        self.y_val = y_val
        self.color = color
    left = None
    right = None
    # weight only applies to range tree
    weight = None
    # box only applies to K-D tree
    box = None
        
# key for sorting list of nodes on their x_val
def getX(p):
    return p.x_val

def getY(p):
    return p.y_val

# returns the root node of a built 1-D range tree
# P: list of points
# D: dictionary of colors and weights
def buildRangeTree(P):
    # base case, P has one point
    # create leaf node, v with value of point and weight of 1
    if len(P) <= 1:
        v = Node(P[0].color, P[0].x_val)
        v.weight = 1
    
    # recursive case, P has more than one point
    else:
        # sort the list and split into two sublists by median point
        P.sort(key=getX)
        if len(P) % 2 == 0:
            mid = (len(P) // 2) - 1
        else:
            mid = len(P) // 2
        P_left = P[:mid + 1]
        P_right = P[mid + 1:]
        
        # create an internal node, v with the value of the median point
        # recursively call buildRangeTree on P's left & right sublists to assign v's left & right children 
        # assign weight of internal node as sum of children's weights
        v = Node(P[mid].color, P[mid].x_val)
        v.left = buildRangeTree(P_left)
        v.right = buildRangeTree(P_right)
        v.weight = v.left.weight + v.right.weight
        
    return v
    
# returns a node inside the query range which splits to all subleafs in query range
# root: root node of 1-D range tree
# Q: query range
def findSplitNodeRangeTree(root, Q):
    v = root
    # loop until node v is at a leaf or is inside the query range
    while (v.left is not None and v.right is not None and (v.x_val >= Q.x_max or v.x_val < Q.x_min)):
        if v.x_val >= Q.x_max:
            v = v.left
        else:
            v = v.right
    return v

# returns a list of the set of all canonical nodes
def findCanonicalSetRangeTree(root, Q):
    # start search from the split node, sp and add valid canonical nodes to the set of all canonical nodes, C
    C = list()
    sp = findSplitNodeRangeTree(root, Q)
   
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

# returns a uniform random node from the set of all canonical nodes in 1-D range tree
# C: set of all canonical nodes in 1-D range tree
def uniformRandomNodeRangeTree(C):
    # concept: returning the node with greatest key is equal to returning a weighted random node
    
    # return if C is empty
    if not C:
        return
    
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

class ColoredWeightedRandomSampling():
    colorDict = dict()
    
    # changes value of colorDict to contain a list of points for each associated color
    # returns transformed list P', where transformed points p' is set to (p, pred(p)) 
    # for each color, pred(p) is defined as predecessor of p in sorted order
    # P: list of points
    def findTransformedList(self, P):
        # create a list of points for every color in P stored in colorDict
        for p in P:     
            key = p.color
            # if the color is in colorDict, append p to list
            if key in self.colorDict.keys():
                self.colorDict[key].append(p)
            # if the color is not in colorDict, create list with p
            else:
                self.colorDict[key] = [p]
                
        P_transformed = list()
        
        # for each colors, access its associated list  
        for key in self.colorDict.keys():
            # for each list, sort list in increasing x_val
            self.colorDict[key].sort(key=getX)
            
            # for each point in list, set the y_val to point's predecessor
            for i in range(len(self.colorDict[key])):
                # if point has no predecessor, set y_val to negative infinity
                if i == 0:
                    self.colorDict[key][i].y_val = -np.inf
                # if point has predecessor, set y_val to previous point's x_val
                else:
                    self.colorDict[key][i].y_val = self.colorDict[key][i - 1].x_val
                # append point's x_val and y_val to P_transformed 
                P_transformed.append(self.colorDict[key][i])
        
        # changes colorDict from containing a list of points to containing a range tree of points
        for key in self.colorDict.keys():
            # for each color, build a range tree using list
            colorRangeTree = buildRangeTree(self.colorDict[key])
            # for each color, set colorDict to its appropriate range tree
            self.colorDict[key] = colorRangeTree
        
        # returns transformed list P
        return P_transformed
    
    # returns the root of K-D tree
    # P: list of transformed points
    # d: depth of tree
    # B: bounding box of root node
    def buildKDTree(self, P, d = None, B = None):
        # at root, set depth to 0
        if d is None:
            d = 0
        # at root, set bounding box to range of P
        if B is None:
            B = BoundingBox(min(P, key=getX).x_val, max(P, key=getX).x_val, min(P, key=getY).y_val, max(P, key=getY).y_val)
            
        # base case, P has one point
        # create leaf node, v with value of point 
        # set v's box to itself
        if len(P) == 1:
            v = Node(P[0].color, P[0].x_val, P[0].y_val)
            v.box = B
        else:
            # depth is even, split box on x_mid (vertical)
            if d % 2 == 0:
                P.sort(key=getX)
                if len(P) % 2 == 0:
                    mid = (len(P) // 2) - 1
                else:
                    mid = len(P) // 2
                P_left = P[:mid + 1]
                P_right = P[mid + 1:]
                
                # create an internal node, v with the value of the median point
                # recursively call buildRangeTree on P's left & right sublists to assign v's left & right children 
                v = Node(P[mid].color, P[mid].x_val, P[mid].y_val)
                v.box = B
                leftBox = BoundingBox(v.box.x_min, v.x_val, v.box.y_min, v.box.y_max)
                rightBox = BoundingBox(v.x_val, v.box.x_max, v.box.y_min, v.box.y_max)
                v.left = self.buildKDTree(P_left, d + 1, leftBox)
                v.right = self.buildKDTree(P_right, d + 1, rightBox)
                
            # depth is odd, split box on y_mid (horizontal)
            else:
                P.sort(key=getY)
                if len(P) % 2 == 0:
                    mid = (len(P) // 2) - 1
                else:
                    mid = len(P) // 2
                P_left = P[:mid + 1]
                P_right = P[mid + 1:]
                
                # create an internal node, v with the value of the median point
                # recursively call buildRangeTree on P's left & right sublists to assign v's left & right children 
                v = Node(P[mid].color, P[mid].x_val, P[mid].y_val)
                v.box = B
                leftBox = BoundingBox(v.box.x_min, v.box.x_max, v.box.y_min, v.y_val)
                rightBox = BoundingBox(v.box.x_min, v.box.x_max, v.y_val, v.box.y_max)
                v.left = self.buildKDTree(P_left, d + 1, leftBox)
                v.right = self.buildKDTree(P_right, d + 1, rightBox)
                
        return v
    
    # returns a list of nodes in root's subtree
    # root: root node of tree 
    def reportSubtree(self, root):
        L = list()
        
        if root is None:
            return L
        
        if root.left is None and root.right is None:
            L = list()
            L.append(root)
            return L 
        else:
            L_left = self.reportSubtree(root.left)
            L_right = self.reportSubtree(root.right)
                    
            if L_left:
                L = L + L_left
            if L_right:
                L = L + L_right
            
            return L
    
    # returns a list of all nodes that satisfy query range
    # root: root node of a two dimensional K-D tree
    # Q: query range
    def queryKDTree(self, root, Q):
        # transform Q from 1-D interval [x_min, x_max] 
        # to 2-D bounding box [x_min, x_max] x (-infinity, x_min)
        L = list()
        if Q.y_min is None:
            Q.y_min = -np.inf
        if Q.y_max is None:
            Q.y_max = Q.x_min
        
        # if root is a leaf, check if root's point intersects Q
        if root.left is None and root.right is None:
            if root.x_val >= Q.x_min and root.x_val <= Q.x_max and root.y_val >= Q.y_min and root.y_val < Q.y_max:
                L = L + self.reportSubtree(root)
            else:
                return L
        # if root is not a leaf
        else:
            # if root's box does not intersect Q, return
            if root.box.x_min > Q.x_max or root.box.x_max < Q.x_min or root.box.y_min >= Q.y_max:
                return L
            
            # if root's box fully intersects Q, append root to list
            elif root.box.x_min >= Q.x_min and root.box.x_max <= Q.x_max and root.box.y_max < Q.y_max:
                L = L + self.reportSubtree(root)
                
            # if root's box partially intersects Q, search root's left and right
            else:          
                L_left = self.queryKDTree(root.left, Q)
                L_right = self.queryKDTree(root.right, Q)
                
                if L_left:
                    L = L + L_left
                if L_right:
                    L = L + L_right
        
        return L

    # returns a weighted random color node
    # L: list of nodes that satisfy query; every node has a unique color
    # Q: query range
    # D: dictionary of colors associated with weights
    def weightedRandomColorNode(self, L, Q, D):
        # return if L is empty
        if not L:
            print('No Nodes found in range')
            return None
        
        # initialize l_max as first element in list
        l_max = L[0]
        l_max_key = np.random.random() ** (1 / D[l_max.color])
        
        # loop from second node to end of L
        # find the node with the greatest key in L and assign to l_max
        for i in range(1, len(L)):
            l = L[i]
            l_key = np.random.random() ** (1 / D[l.color])
            # replace l_max and l_max_key if the current node in the list has a greater key
            if l_key > l_max_key:
                l_max = l
                l_max_key = l_key
        
        # search the range tree of l_max's color and find a random node that satisfies query range
        canonicalNodes = findCanonicalSetRangeTree(self.colorDict[l_max.color], Q)
        v = uniformRandomNodeRangeTree(canonicalNodes) 
        
        return v
        

# ----------------------------------------------------------------------------------------------------------------
# example usage of uniform random sampling

# database is a list of one dimensional nodes to use as database
database = list()
databaseSize = 1000
colorWeightDict = {'red': 2, 'blue': 3, 'yellow': 4, 'green': 5, 'orange': 6, 'purple': 7}
for i in range(databaseSize):
    random = np.random.randint(0, 6)
    if random == 0:
        database.append(Node('red', i))
    elif random == 1:
        database.append(Node('blue', i))
    elif random == 2: 
        database.append(Node('yellow', i))
    elif random == 3: 
        database.append(Node('green', i))
    elif random == 4: 
        database.append(Node('orange', i))
    elif random == 5: 
        database.append(Node('purple', i))
            
# create ColoredWeightedRandomSampling class and transform database
cwrs = ColoredWeightedRandomSampling() 
transformedDatabase = cwrs.findTransformedList(database)

# build kd tree and one dimensional query range
kdTree = cwrs.buildKDTree(database)
queryRange = BoundingBox(300, 500)

# query the kd tree and find a random node from that query result
nodes = cwrs.queryKDTree(kdTree, queryRange)
randomNode = cwrs.weightedRandomColorNode(nodes, queryRange, colorWeightDict)
print('Random node:', randomNode.x_val, randomNode.color)
print('# colors in K-D tree: ', len(nodes), '\n')

# ----------------------------------------------------------------------------------------------------------------
# test below proves weightedRandomColorNode has a distribution proportional to the weights of colors

freqList = list()
numIterations = 10000

for i in range(len(cwrs.colorDict)):
    freqList.append(0)
    
for i in range(numIterations):
    randomNode = cwrs.weightedRandomColorNode(nodes, queryRange, colorWeightDict)
    
    if randomNode.color == 'red':
        freqList[0] = freqList[0] + 1
    if randomNode.color == 'blue':
        freqList[1] = freqList[1] + 1
    if randomNode.color == 'yellow':
        freqList[2] = freqList[2] + 1
    if randomNode.color == 'green':
        freqList[3] = freqList[3] + 1
    if randomNode.color == 'orange':
        freqList[4] = freqList[4] + 1
    if randomNode.color == 'purple':
        freqList[5] = freqList[5] + 1

print('Frequencies of colors (actual - theoretical):')
print('red    %:', freqList[0] / numIterations, '-', math.trunc(2/27*10000)/10000)
print('blue   %:', freqList[1] / numIterations, '-', math.trunc(3/27*10000)/10000)
print('yellow %:', freqList[2] / numIterations, '-', math.trunc(4/27*10000)/10000)
print('green  %:', freqList[3] / numIterations, '-', math.trunc(5/27*10000)/10000)
print('orange %:', freqList[4] / numIterations, '-', math.trunc(6/27*10000)/10000)
print('purple %:', freqList[5] / numIterations, '-', math.trunc(7/27*10000)/10000)

freqTable = {}
x_min = None

for i in range(numIterations):
    randomNode = cwrs.weightedRandomColorNode(nodes, queryRange, colorWeightDict)
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

print('\nRange of random nodes (actual - theoretical):')
print('[' + str(x_min) + ',' + str(x_max) + '] - [' + str(queryRange.x_min) + ',' + str(queryRange.x_max) + ']')

