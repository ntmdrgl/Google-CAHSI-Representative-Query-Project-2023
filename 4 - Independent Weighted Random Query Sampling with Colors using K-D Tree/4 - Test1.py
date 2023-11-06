# # -*- coding: utf-8 -*-

import IWRS.Code as iwrs 
import math

databaseSize = 1000
numColors = 10 

# assign weights to colors
colorWeightDict = dict()
for i in range(1, numColors + 1):
    colorWeightDict[str(i)] = 1000 * (0.5 * math.exp(-0.5 * i))

# create a database of colored 1-D points
database = list()
for i in range(1, databaseSize + 1):
    database.append(iwrs.Node(str(i % numColors + 1), i))

# create class
cwrs = iwrs.ColoredWeightedRandomSampling(colorWeightDict)

# create a transformed database with 2-D points
transformedDatabase = cwrs.findTransformedList(database)

# build kdtree, define query range, find canonical nodes
kdTree = cwrs.buildKDTree(transformedDatabase)
queryRange = iwrs.BoundingBox(41, 83)
canonicalNodes = cwrs.queryKDTree(kdTree, queryRange)

# initialize counts of colors to 0
colorCounts = list()
for i in range(numColors):
    colorCounts.append(0)

# find color counts of random nodes after many iterations
numIterations = 1000
for i in range(numIterations):
    randomNode = cwrs.weightedRandomColorNode(canonicalNodes, queryRange)
    if randomNode is None:
        continue
    colorCounts[int(randomNode.color) - 1] = colorCounts[int(randomNode.color) - 1] + 1
    
# print frequencies of colors
for i in range(1, numColors + 1):
    print(i, '%:', colorCounts[i - 1] / numIterations)
    
