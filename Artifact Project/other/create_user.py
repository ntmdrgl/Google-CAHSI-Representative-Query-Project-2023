# -*- coding: utf-8 -*--
"""
Created on March 6, 2024
Authors: Alexander Madrigal, Nathaniel Madrigal

"""

import mysql.connector
from getpass import getpass
from mysql.connector import Error

def create_user(first_name, last_name, birthday):
    create_user = """
        INSERT INTO users (first_name, last_name, birthday) VALUES
        (%s, %s, %s);
    """
    val_tuple = (
        first_name,
        last_name,
        birthday    
    )
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
        mycursor.execute(create_user, val_tuple)
        result = mycursor.fetchall()
        connection.commit()
        print('User created successfully')
    except Error as e:
        print(e)
    
    
    
    
