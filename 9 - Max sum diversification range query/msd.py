# -*- coding: utf-8 -*-
"""
Created on: May 20, 2024
Authors: Nathaniel Madrigal, Alexander Madrigal
"""

import numpy as np
import math
import heapq

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
def msd(points, num_dim, k):
    # generate a certain number of vectors as "surface points" 
    num_surface_points = len(points)
    surface_points = generate_vector_points(num_surface_points, num_dim)
    
    # turn surface points into the vector class assigning a twin and filling their max heaps
    vectors = list()
    for sp in surface_points:
        v = Vector(sp)
        v_twin = Vector(np.multiply(sp, -1)) # vector twin has opposite direction
        v.twin = v_twin
        
        # if the inner product between the surface point and inner point is positive, 
        #   add inner point to max heap of v
        # else add inner point to max heap of v_twin
        # max heaps are sorted on the inner products between the vector coordinate and inner points
        for p in points:
            inner_product = np.inner(sp, p)
            if inner_product >= 0:
                heapq.heappush(v.max_heap, (inner_product * -1, p))
            else:
                heapq.heappush(v_twin.max_heap, (np.inner(v_twin.coord, p) * -1, p))
        
        vectors.append(v)
        # vectors.append(v_twin)
        
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

num_points = 1000
num_dim = 3
k = 10

# generate a random set of points inside of a sphere
inner_points = list()
for i in range(num_points):
    while True:
        x = np.random.uniform(size=num_dim)
        h = 0
        for j in range(0, num_dim):
            h += math.pow(x[j], 2)    
        h = math.sqrt(h)
        # ensure point is inside of sphere
        if h < 1:
            inner_points.append(x)
            break

result = msd(inner_points, num_dim, k)
print("msd result:", result)
    