# Uniform Random Query Sampling using 1-D Range Tree

Functionality:
- Builds a one dimensional range tree from a list of one dimensional points
- Randomly samples a point within a query interval

Restrictions:
- All values in list of one dimensional points must be distinct

# How to use
1. Build a range tree using buildRangeTree function with a list of nodes as input
2. Build a list of canonical nodes for a specific query interval using findCanonicalSet function
    - Inputs the root of a range tree and a query interval (defined by QueryRange class)
    - Rebuild the list of canonical nodes to search through a new query interval
3. Using uniformRandomNode function, return a random node within the query interval with a list of canonical nodes as input
    
# Concept for uniform random sampling
- Definitions of terms used
    - Canonical node: node where subtree rooted at that node only contains points contained in the query
    - Weight: an object of node v which contains the number of leaves in a subtree rooted at v
    - Key: a random float from 0 to 1 to the power of 1 over a weight
    
1. Recursively assign weights of nodes when building the range tree:
    - Base case: leaf nodes have a weight of 1 
    - Recursive case: the weight of an internal node is the sum of its children's weights 
2. Find and append every canonical node into a list
3. Randomly chose a canonical node from the built list of canonical nodes with probrability associated with each canonical node's weight
    - Calculate the key for every canonical node
    - Chose the canonical node with the greatest key
4. Randomly chose a leaf from the subtree rooted at the chosen canonical node with probrability associated with each leaf node's weight
    - Traverse down the path with the greatest key
    - The leaf node at the end of the path satisfies the condition of being a uniform random sample inside of the query interval