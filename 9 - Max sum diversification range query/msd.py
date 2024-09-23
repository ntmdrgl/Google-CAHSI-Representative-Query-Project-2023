# -*- coding: utf-8 -*-
"""
Created on: May 20, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal
"""

import numpy as np
import math
import heapq
import time
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
import matplotlib.patches as mpatches 

# generate a random set of vectors represented by points on the surface of a d-dimensional sphere
def generate_vector_points(num_vectors, num_dim):
    surface_points = list()
    for i in range(num_vectors):
        # generate standard normal for d coordinates
        x = np.random.normal(loc=0, scale=1, size=(num_dim))   
        # construct a unit vector
        h = 0
        for j in range(0, num_dim):
            h += math.pow(x[j], 2)    
        h = math.sqrt(h)    
        surface_points.append(np.divide(x, h))
    return surface_points

# each vector creates a twin vector in the opposite direction
# each vector stores a max heap of points in order of inner product from vector coordinate
class Vector():
    def __init__(self, coord):
        self.coord = coord               
        self.twin = None
        self.max_heap = list()
    
# returns k points with approximately max-sum distance
def msd(points, num_dim, k, num_vectors):
    # generate a certain number of vectors as "surface points" 
    num_surface_points = num_vectors
    surface_points = generate_vector_points(num_surface_points, num_dim)
    
    # turn surface points into the vector class assigning a twin and filling their max heaps
    vectors = list()
    for sp in surface_points:
        v = Vector(sp)
        v_twin = Vector(np.multiply(sp, -1)) # vector twin has opposite direction
        v.twin = v_twin
        
        topk_min_heap = list()
        for p in points:
            inner_product = np.inner(sp, p)
        
            if len(topk_min_heap) < k:
                heapq.heappush(topk_min_heap, (np.inner(sp, p) * +1, p))
            elif len(topk_min_heap) == k: 
                if inner_product > topk_min_heap[0][0]:
                    heapq.heapreplace(topk_min_heap, (np.inner(sp, p) * +1, p))
        
        # max heaps are sorted on the inner products between the vector coordinate and inner points
        for (inner, p) in topk_min_heap:
            heapq.heappush(v.max_heap, (np.inner(sp, p) * -1, p))
            heapq.heappush(v_twin.max_heap, (np.inner(v_twin.coord, p) * -1, p))
        
        vectors.append(v)
        # vectors.append(v_twin)
        
    if num_dim == 2:
        xs = list()
        ys = list()
        for v in vectors:
            [x, y] = v.coord
            xs.append(x)
            ys.append(y)
        figure(figsize=(5,5), dpi=80)
        plt.title(f"Random vectors (num vectors = {num_vectors})")
        plt.xlim(-1,1)
        plt.ylim(-1,1)
        plt.scatter(xs, ys, color = 'green')
        
    # take k/2 passes
    msd_points = list()
    for i in range(k // 2):
        # find a point on top of heap and point on top of twin's heap such that
        #   the sum of the inner products is the greatest
        max_sum_inner_product = 0
        max_point = None
        max_twin_point = None
        for v in vectors:
            # check all vectors as possible candidates
            v_twin = v.twin
            curr_inner = None
            curr_twin_inner = None
            curr_point = None
            curr_twin_point = None
            
            # take the top element from v's max heap
            #   make sure the point on top was not already inserted into msd_points (final result)
            #   if so, repeat and take another element on top
            while(True):
                if not v.max_heap:
                    break
                (inner, p) = heapq.heappop(v.max_heap)
                p = p.tolist()
                if p in msd_points:
                    continue
                else:
                    curr_inner = inner
                    curr_point = p
                    break
                
            # repeat for twin's heap
            while(True):
                if not v_twin.max_heap:
                    break
                (inner, p) = heapq.heappop(v_twin.max_heap)
                p = p.tolist()
                if p in msd_points:
                    continue
                else:
                    curr_twin_inner = inner
                    curr_twin_point = p
                    break
                
            if curr_inner is not None and curr_twin_inner is not None:
                # compare sums of inner products and make max if greater
                sum_inner_product = (curr_inner * -1) + (curr_twin_inner * -1)
                if sum_inner_product > max_sum_inner_product:
                    max_sum_inner_product = sum_inner_product
                    max_point = curr_point
                    max_twin_point = curr_twin_point
            
        msd_points.append(max_point)
        msd_points.append(max_twin_point)
        
    return msd_points

# returns k points with approximately max-sum distance
def msd_greedy(points, num_dim, k):
    msd_points = list()
    
    for i in range(k // 2):
        farthest_distance = 0
        farthest_idx = 0
        for j, x in enumerate(points):
            curr_distance = 0
            for k_it in range(0, num_dim):
                curr_distance += (x[k_it] - points[0][k_it])**2
            curr_distance = math.sqrt(curr_distance)    
                        
            if curr_distance > farthest_distance:
                farthest_distance = curr_distance
                farthest_idx = j
                
        if farthest_idx != 0:
            msd_points.append(points[0])
            msd_points.append(points[farthest_idx])
            
            del points[farthest_idx]
            del points[0]
        else:
            print("ERROR")
    
    return msd_points
    
def div_score(points):
    score = 0
    for p in points:
        for q in points:
            if (p is q) or (p is None) or (q is None):
                continue
            [x1, y1] = p
            [x2, y2] = q
            score += math.sqrt((x2-x1)**2 + (y2-y2)**2)
    return score

num_points = 30
num_dim = 2
k = 5

print(f"num_points: {num_points}")
print(f"num_dim:    {num_dim}")
print(f"k:          {k}")
print()

# generate a random set of points inside of a sphere
inner_points = list()
for i in range(num_points):
    while True:
        x = np.random.uniform(low=-1, high=1, size=num_dim)
        # inner_points.append(x)
        # break
        h = 0
        for j in range(0, num_dim):
            h += math.pow(x[j], 2)    
        h = math.sqrt(h)
        # ensure point is inside of sphere
        if h < 1:
            inner_points.append(x)
            break

if num_dim == 2:
    xs = list()
    ys = list()
    for p in inner_points:
        [x, y] = p
        xs.append(x)
        ys.append(y)
    figure(figsize=(5,5), dpi=80)
    plt.title("Random points in circle")
    plt.xlim(-1,1)
    plt.ylim(-1,1)
    plt.scatter(xs, ys, color = 'orange')

times = list()
scores = list()

for epsilon in [0.3, 0.2, 0.1, 0.05, 0.025]:
    num_vectors = int(1 / (epsilon ** num_dim))
    print(f"num vectors (epsilon = {round(epsilon, 3)}):", num_vectors)
    
    t_start = time.time_ns()
    result = msd(inner_points.copy(), num_dim, k, num_vectors)
    t_end = time.time_ns()
    times.append((t_end - t_start) / (10 ** 9))
    
    scores.append(div_score(result))
    
    # print("MSD result size:", len(result))
    # if len(result) == k:
    #     print("Same number of points as k")
    # else:
    #     print("ERROR: incorrect number of points")
    
    if num_dim == 2:
        xs = list()
        ys = list()
        cs = list()
        is_twin = False
        
        for p in result:
            if p is not None:
                [x, y] = p
                xs.append(x)
                ys.append(y)
                if is_twin:
                    cs.append("red")
                else:
                    cs.append("blue")
                is_twin = not is_twin
                
        figure(figsize=(5,5), dpi=80)
        plt.title(f"Points from New MSD algorithm (epsilon = {round(epsilon, 3)})")
        plt.xlim(-1,1)
        plt.ylim(-1,1)
        blue_patch = mpatches.Patch(color='blue', label='max point of vector v') 
        red_patch = mpatches.Patch(color='red', label='max point of vector -v') 
        plt.legend(handles=[blue_patch, red_patch]) 
        plt.scatter(xs, ys, color = cs)

t_start = time.time_ns()
result = msd_greedy(inner_points.copy(), num_dim, k)
t_end = time.time_ns()
times.append((t_end - t_start) / (10 ** 9))

scores.append(div_score(result))

# print("MSD result size:", len(result))
# if len(result) == k:
#     print("Same number of points as k")
# else:
#     print("ERROR: incorrect number of points")

if num_dim == 2:
    xs = list()
    ys = list()
    cs = list()
    is_twin = False
    for p in result:
        [x, y] = p
        xs.append(x)
        ys.append(y)
        if is_twin:
            cs.append("red")
        else:
            cs.append("blue")
        is_twin = not is_twin
        
    figure(figsize=(5,5), dpi=80)
    plt.title("Points from Simple MSD algorithm")
    plt.xlim(-1,1)
    plt.ylim(-1,1)
    blue_patch = mpatches.Patch(color='blue', label='randomly chosen point v') 
    red_patch = mpatches.Patch(color='red', label='point with farthest distance from v') 
    plt.legend(handles=[blue_patch, red_patch]) 
    plt.scatter(xs, ys, color = cs)
    plt.show()
    
    
    
# max diversity algorithm

max_score = 0

def combinationUtil(arr, n, r, 
                    index, data, i):
    global max_score
    if(index == r):
        for j in range(r):
            curr_score = div_score(data)
            if curr_score > max_score:
                max_score = curr_score
        return
    
    if(i >= n):
        return
 
    data[index] = arr[i]
    combinationUtil(arr, n, r, 
                    index + 1, data, i + 1)
     
    combinationUtil(arr, n, r, index, 
                    data, i + 1)
    
arr = inner_points
data = list(range(k))
# print(len(inner_points), num_points)
# print(inner_points)
combinationUtil(arr, num_points, k, 0, data, 0)
scores.append(max_score)

# arr = [10, 20, 30, 40, 50]
# r = 3
# n = len(arr)
# data = list(range(r))
# combinationUtil(arr, n, r, 0, data, 0)

# time bar graph
print(f"\ntimes: {times}")
plt.bar(range(1, len(times) + 1), times, color='green')
plt.title("New vs N^2 MSD Times")
plt.xlabel('Different msd algorithms (1-5:new 6:simple)')
plt.ylabel('Time')
plt.show()

# score bar graph
print(f"scores: {scores}")
plt.bar(range(1, len(scores) + 1), scores, color='purple')
plt.title("Diversity scores of MSD algorithms")
plt.xlabel('Different msd algorithms (1-5:new 6:simple 7:max)')
plt.ylabel('Diversity Score')
plt.show()