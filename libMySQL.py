# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import mysql.connector
import pandas as pd
from mysql.connector import Error

from config import Config

DATABASE_HOSTNAME = Config.DATABASE_HOSTNAME
DATABASE_PORT = Config.DATABASE_PORT
DATABASE_PASSWORD = Config.DATABASE_PASSWORD
DATABASE_NAME = Config.DATABASE_NAME
DATABASE_USERNAME = Config.DATABASE_USERNAME


def create_server_connection(host_name, port_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            port=port_name,
            user=user_name,
            passwd=user_password,
            database=db_name,
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection


db = create_server_connection(
    DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)


def MySQL_Select(query,val):
    cursor = db.cursor(dictionary=True)
    # cursor = db.cursor()
    result = None
    try:
        cursor.execute(query,val)
        result = cursor.fetchall()
        return result
    except Error as err:
        cursor.close()
        print(f"Error: '{err}'")


def MySQL_Insert(query):
    cursor = db.cursor(dictionary=True)
    # cursor = db.cursor()
    result = None
    try:
        cursor.execute(query)
        db.commit()
        result = cursor.rowcount
        print(result, "Record inserted successfully into Laptop table")
        return result
    except Error as err:
        cursor.close()
        print(f"Error: '{err}'")
    finally:
        # closing database connection.
        if db.is_connected():
            # db.close()
            print("connection is closed")


def MySQL_Update(query):
    cursor = db.cursor(dictionary=True)
    # cursor = db.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        db.commit()
        result = cursor.rowcount
        print("Record Updated successfully ")
        return result
    except Error as err:
        cursor.close()
        print(f"Error: '{err}'")


def MySQL_Delete(query):
    cursor = db.cursor(dictionary=True)
    # cursor = db.cursor()
    result = None
    try:
        cursor.execute(query)
        db.commit()
        result = cursor.rowcount
        print('number of rows deleted', result)
        return result
    except Error as err:
        print(f"Error: '{err}'")
