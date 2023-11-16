# -*- coding: utf-8 -*-
"""
Created on: November 16, 2023
Authors: Alexander Madrigal, Nathaniel Madrigal

source: https://archive.ics.uci.edu/dataset/2/adult
"""

import pandas as pd

# name all 15 columns of data
columnNames = ['age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 'occupation', 'relationship', 'race', 'sex', 'capital-gain', 'capital-loss', 'hours-per-week', 'native-country', 'income']
# name selected 6 numerical columns (dimensions)
columnsUsedNum = ['age', 'fnlwgt', 'education-num', 'capital-gain', 'capital-loss', 'hours-per-week']
# name selected 2 categorical columns (colors) 
columnsUsedColor = ['race', 'sex']
# read csv file, comma seperated, no header in csv file, set names of columns, set used columns
dataNum = pd.read_csv('adult.data', sep=',', header=None, names=columnNames, usecols=columnsUsedNum)
dataColor = pd.read_csv('adult.data', sep=',', header=None, names=columnNames, usecols=columnsUsedColor)
# generate dataframe using data
dataframeNum = pd.DataFrame(dataNum)
dataframeColor = pd.DataFrame(dataColor)

print(dataframeNum)
print(dataframeColor)

#generate dataset (list of lists) from dataframe
datasetNum = dataframeNum.to_numpy().tolist()
datasetColor = dataframeColor.to_numpy().tolist()

races = ['White', 'Asian-Pac-Islander', 'Amer-Indian-Eskimo', 'Other', 'Black']
sexes = ['Male', 'Female']

for S in datasetNum:
    for i in range(0, len(S)):
        if i == 0:
            # print(S[i], end=" ")
            pass
        
    

