# -*- coding: utf-8 -*-
"""
Created on: November 16, 2023
Authors: Alexander Madrigal, Nathaniel Madrigal


"""

import pandas as pd

columnNames = ['age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 'occupation', 'relationship', 'race', 'sex', 'capital-gain', 'capital-loss', 'hours-per-week', 'native-country', 'income']
columnsUsed = ['age', 'fnlwgt', 'education-num', 'race', 'sex', 'capital-gain', 'capital-loss', 'hours-per-week']
# read csv file
data = pd.read_csv('adult.data', sep=',', header=None, names=columnNames, usecols=columnsUsed)
dataframe = pd.DataFrame(data)
print(dataframe)

dataset = dataframe.values.tolist()
# dimensions at indexes 0, 1, 2, 5, 6, 7 (total 6)
# colors at indexes 3, 4  (total unique combinations 10)


