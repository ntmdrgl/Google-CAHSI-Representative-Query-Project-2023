# Dependent Weighted Random Sampling with Colors using 1-D Range Tree

Functionality:
- Builds a one dimensional range tree from a list of one dimensional colored points
    - each color corresponds to a weight
- Randomly samples a point within a query interval with probability associated with weights of colors

Restrictions:
- All values in list of one dimensional points must be distinct
- Random sampling is dependent on query interval
    - The same query interval will provide the same output 

# How to use
1. 
    
# Concept for uniform random sampling
- Definitions of terms used
    - Canonical node: node where subtree rooted at that node only contains points contained in the query
    - Weight: an object of node v which contains the number of leaves in a subtree rooted at v
    - Key: a random float from 0 to 1 to the power of 1 over a weight
    
1. 