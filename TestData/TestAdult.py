# -*- coding: utf-8 -*-
"""
Created on: November 16, 2023
Authors: Alexander Madrigal, Nathaniel Madrigal


"""

import pandas as pd

# name all 15 columns of data
columnNames = ['age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 'occupation', 'relationship', 'race', 'sex', 'capital-gain', 'capital-loss', 'hours-per-week', 'native-country', 'income']
# name all 8 columns needed
columnsUsed = ['age', 'fnlwgt', 'education-num', 'race', 'sex', 'capital-gain', 'capital-loss', 'hours-per-week']
# read csv file, comma seperated, no header in csv file, set names of columns, set used columns
data = pd.read_csv('adult.data', sep=',', header=None, names=columnNames, usecols=columnsUsed)
# generate dataframe using data
dataframe = pd.DataFrame(data)
print(dataframe) # uncomment to glimse at entire dataset

#generate dataset (list of lists) from dataframe
dataset = dataframe.to_numpy().tolist()
# dimensions at indexes 0, 1, 2, 5, 6, 7 (total 6)
# colors at indexes 3, 4  (total unique combinations 10)

races = ['White', 'Asian-Pac-Islander', 'Amer-Indian-Eskimo', 'Other', 'Black']
sexes = ['Male', 'Female']

for S in dataset:
    for i in range(0, len(S)):
        if i == 0:
            # print(S[i], end=" ")
            pass
        
    

