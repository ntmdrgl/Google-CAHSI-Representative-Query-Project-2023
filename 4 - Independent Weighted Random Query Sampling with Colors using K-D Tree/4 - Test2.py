# -*- coding: utf-8 -*-

import IWRS.Code as iwrs 
from matplotlib import pyplot as plt
import time
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
    if i < 41 or i > 83:
        database.append(iwrs.Node(str(i % numColors + 1), i))
    else:
        if i >= 41 and i <= 44:
            database.append(iwrs.Node(str(i - 40), i))
        elif i >= 79 and i <= 83:
            database.append(iwrs.Node(str(89 - i), i))
        else:
            database.append(iwrs.Node(str(5), i))

# create class
cwrs = iwrs.ColoredWeightedRandomSampling(colorWeightDict)

# create a transformed database with 2-D points
transformedDatabase = cwrs.findTransformedList(database)

# build kdtree, define query range, find canonical nodes
t = time.time_ns()
kdTree = cwrs.buildKDTree(transformedDatabase)
print('Build time:', (time.time_ns() - t) / (10 ** 6), 'ms')
queryRange = iwrs.BoundingBox(41, 83)
canonicalNodes = cwrs.queryKDTree(kdTree, queryRange)

# initialize counts of colors to 0
colorCounts = list()
for i in range(numColors):
    colorCounts.append(0)

# find color counts of random nodes after many iterations
numIterations = 1000
t = time.time_ns()
for i in range(numIterations):
    randomNode = cwrs.weightedRandomColorNode(canonicalNodes, queryRange)
    if randomNode is None:
        continue
    colorCounts[int(randomNode.color) - 1] = colorCounts[int(randomNode.color) - 1] + 1
print('Avg query time:', ((time.time_ns() - t) / (10 ** 6)) / numIterations, 'ms')

# find frequencies of colors
colorFreqs = [None] * numColors
for i in range(numColors):
    colorFreqs[i] = colorCounts[i] / numIterations

plt.bar(range(1, numColors + 1), colorFreqs, color='orange')
plt.title('Test 2: Frequencies of colors from random query sampling')
plt.xlabel('Color')
plt.ylabel('Frequency')
plt.show()