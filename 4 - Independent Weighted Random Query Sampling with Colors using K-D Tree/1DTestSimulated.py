# -*- coding: utf-8 -*-

import IWRS.Code as iwrs 
from matplotlib import pyplot as plt
import time
import math

databaseSize = 100000
numColors = 5

# assign weights to colors
colorWeightDict = dict()
color_weight_list = list()
for i in range(1, numColors + 1):
    colorWeightDict[str(i)] = 1000 * (0.7 * math.exp(-0.7 * i))
    color_weight_list.append(1000 * (0.7 * math.exp(-0.7 * i)))  

# create a database of colored 1-D points
color_freq_list = [0.2] * numColors
database = list()
for i in range(1, databaseSize + 1):
    database.append(iwrs.Node(str(i % numColors + 1), i))

# for it in range(numColors):
#     color_freq_list[it] /= len(database)

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
numIterations = 10000
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

plt.bar(range(1, numColors + 1), color_freq_list, color='green')
plt.title('Frequencies of colors in dataset')
plt.xlabel('Color')
plt.ylabel('Frequencies')
plt.show()

plt.bar(range(1, numColors + 1), color_weight_list, color='blue')
plt.title('Weights of colors')
plt.xlabel('Color')
plt.ylabel('Weight')
plt.show()

plt.bar(range(1, numColors + 1), colorFreqs, color='orange')
plt.title('Frequencies of colors from random query sampling')
plt.xlabel('Color')
plt.ylabel('Frequency')
plt.show()   

print("color freq in dataset:")
for i in color_freq_list:
    print(i)

print("\ncolor weights:")
for i in color_weight_list:
    print(i)

print("\ncolor freq from samples:")
for i in colorFreqs:
    print(i)
