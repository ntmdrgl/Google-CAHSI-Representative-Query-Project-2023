# -*- coding: utf-8 -*-
"""
Created on January 23, 2024
Authors: Alexander Madrigal and Nathaniel Madrigal
"""

import numpy as np
import pandas as pd
import math
import time
from matplotlib import pyplot as plt

data = pd.read_csv('2d_dataset.txt', sep=',', header=None, names=['x', 'y'], low_memory=False)

dataframe = pd.DataFrame(data)

dataset = dataframe.to_numpy().tolist()
