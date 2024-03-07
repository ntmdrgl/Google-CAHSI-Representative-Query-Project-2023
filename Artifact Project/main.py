# -*- coding: utf-8 -*--
"""
Created on March 6, 2024
Authors: Alexander Madrigal, Nathaniel Madrigal

"""

import mysql.connector
from getpass import getpass
from mysql.connector import Error

import create_user 

create_user.create_user("Nathaniel", "Madrigal", "2005-04-19")