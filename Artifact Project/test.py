# -*- coding: utf-8 -*--
"""
Created on March 6, 2024
Authors: Alexander Madrigal, Nathaniel Madrigal

"""

import mysql.connector
from getpass import getpass
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host="localhost",
        # user=input("Enter username: "),
        # password=getpass("Enter password: "),
        user="root",
        password="Password123!",
        database="artifactdb"
    ) 
    mycursor = connection.cursor()
    
    #1. Describe data and see schema
    
    describe_users = "DESCRIBE users"
    mycursor.execute(describe_users)
    result = mycursor.fetchall()
    # for row in result:
    #     print(row)
    
    
    #2. Insert data into tables using executemany
    
    insert_users_query = """
        INSERT INTO users (user_id, first_name, last_name, birthday)
        VALUES (%s,%s, %s, %s)
    """
    users_record = [
        (103, 'Nathaniel', 'Madrigal', '2005-04-19'), 
        (104, 'Eliana', 'Madrigal', '2012-09-14')
    ]
    # mycursor.executemany(insert_users_query, users_record)
    # connection.commit()
    
    
    #3. Select data from tables
    select_users_query = "SELECT * FROM users"
    mycursor.execute(select_users_query)
    for users_result in mycursor.fetchmany(5):
        print(users_result)
    mycursor.fetchall()
        
        
    
except Error as e:
    print(e)


