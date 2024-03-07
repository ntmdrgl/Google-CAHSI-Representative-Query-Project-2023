# -*- coding: utf-8 -*-
"""
Created on March 6, 2024
Authors: Alexander Madrigal, Nathaniel Madrigal

"""

import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Password123!",
  database="artifactdb"
)

mycursor = mydb.cursor()

mycursor.execute("SHOW TABLES")

for x in mycursor:
  print(x)