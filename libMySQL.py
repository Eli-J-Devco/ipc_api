# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import time

import mysql.connector
import pandas as pd
from mysql.connector import Error

from config import Config

DATABASE_HOSTNAME = Config.DATABASE_HOSTNAME
DATABASE_PORT = Config.DATABASE_PORT
DATABASE_PASSWORD = Config.DATABASE_PASSWORD
DATABASE_NAME = Config.DATABASE_NAME
DATABASE_USERNAME = Config.DATABASE_USERNAME

# print(f'DATABASE_HOSTNAME: {DATABASE_HOSTNAME}')
# print(f'DATABASE_PORT: {DATABASE_PORT}')
# print(f'DATABASE_PASSWORD: {DATABASE_PASSWORD}')
# print(f'DATABASE_NAME: {DATABASE_NAME}')
# print(f'DATABASE_USERNAME: {DATABASE_USERNAME}')


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
        # print("MySQL Database connection successful")
    except Exception as err:
        print(f"Error: '{err}'")

    return connection



async def MySQL_Select_v1(query):
    db = create_server_connection(
        DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    if db :
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            # print(result)
            cursor.close()
            db.close()
            return result
        except Exception as err:
            cursor.close()
            db.close()
            print(f"Error: '{err}'")
    else :
        while True :
            time.sleep(1)

        
def MySQL_Select(query,val):
    db = create_server_connection(
    DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    if db :
        cursor = db.cursor(dictionary=True)
        # cursor = db.cursor()
        result = None
        try:
            cursor.execute(query,val)
            result = cursor.fetchall()
            cursor.close()
            db.close()
            return result
        except Exception as err:
            cursor.close()
            db.close()
            print(f"Error: '{err}'")
    else :
        while True :
            time.sleep(1)
def MySQL_Insert(query):
    db = create_server_connection(
    DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    cursor = db.cursor(dictionary=True)
    # cursor = db.cursor()
    result = None
    try:
        cursor.execute(query)
        db.commit()
        result = cursor.rowcount
        print(result, "Record inserted successfully into Laptop table")
        cursor.close()
        db.close()
        return result
    except Exception as err:
        cursor.close()
        db.close()
        print(f"Error: '{err}'")
    finally:
        # closing database connection.
        if db.is_connected():
            # db.close()
            print("connection is closed")
            
def MySQL_Insert_v1(query,val):
    db = create_server_connection(
    DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    cursor = db.cursor(dictionary=True)
    # cursor = db.cursor()
    result = None
    try:
        cursor.execute(query,val)
        db.commit()
        result = cursor.rowcount
        # print("Sync data successfully---> ")
        cursor.close()
        db.close()
        return result
    except Exception as err:
        cursor.close()
        db.close()
        print(f"Error: '{err}'")
    finally:
        # closing database connection.
        if db.is_connected():
            # db.close()
            print("connection is closed")
            
def MySQL_Insert_v2(table_name,len_val,val):
    db = create_server_connection(
    DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    # cursor = db.cursor(dictionary=True)
    cursor = db.cursor()
    result = None
    try:
        # Create a list of columns
        columns = ['time', 'id_device']
        for i in range(len(len_val)):
            columns.append(f'pt{i}')
        print(columns)
        # Create a query
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
        
        cursor.execute(query, val)
        db.commit()
        result = cursor.rowcount
        # print("Successfully inserted data into the database table---> ")
        cursor.close()
        db.close()
        return result
    except Exception as err:
        cursor.close()
        db.close()
        print(f"Error: '{err}'")
    finally:
        # closing database connection.
        if db.is_connected():
            # db.close()
            print("connection is closed")

def MySQL_Insert_v3(data):
    db = create_server_connection(DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    cursor = db.cursor(dictionary=True)
    result = None
    try:
        for key, value in data.items():
            sql = value[0]
            val = value[1]
            cursor.execute(sql, val)
            print("Data inserted successfully")
        
        db.commit()
        result = cursor.rowcount
        # print("Sync data successfully---> ")
        cursor.close()
        db.close()
        return result
    except Exception as err:
        cursor.close()
        db.close()
        print(f"Error: '{err}'")
    finally:
        # closing database connection.
        if db.is_connected():
            print("connection is closed")
def MySQL_Insert_v4(query,val):
    db = create_server_connection(
    DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)

    cursor = db.cursor(dictionary=True)
    # cursor = db.cursor()
    result = None
    try:
        cursor.executemany(query,val)
        db.commit()
        result = cursor.rowcount
        print("Sync data successfully---> ")
        cursor.close()
        db.close()
        return result
    except Exception as err:
        cursor.close()
        db.close()
        print(f"Error: '{err}'")
        
    finally:
        # closing database connection.
        if db.is_connected():
            # db.close()
            print("connection is closed")
            
            
def MySQL_Update(query):
    db = create_server_connection(
    DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)

    cursor = db.cursor(dictionary=True)
    # cursor = db.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        db.commit()
        result = cursor.rowcount
        #print("Record Updated successfully ")
        cursor.close()
        db.close()
        return result
    except Exception as err:
        cursor.close()
        db.close()
        print(f"Error: '{err}'")
        
def MySQL_Update_V1(query,val):
    db = create_server_connection(
    DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)

    cursor = db.cursor(dictionary=True)
    # cursor = db.cursor()
    result = None
    try:
        cursor.execute(query,val)
        result = cursor.fetchall()
        db.commit()
        result = cursor.rowcount
        # print("Record Updated successfully ")
        cursor.close()
        db.close()
        return result
    except Exception as err:
        cursor.close()
        db.close()
        print(f"Error: '{err}'")

def MySQL_Update_v2(query, val):
    db = create_server_connection(
    DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)

    cursor = db.cursor(dictionary=True)
    result = None
    try:
        cursor.executemany(query, val)
        db.commit()
        result = cursor.rowcount
        # print("Data updated successfully",query ,val)
        cursor.close()
        db.close()
        return result
    except Exception as err:
        cursor.close()
        db.close()
        print(f"Error: '{err}'")
    finally:
        if db.is_connected():
            print("Connection is closed")
            
def MySQL_Delete(query):
    db = create_server_connection(
    DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)

    cursor = db.cursor(dictionary=True)
    # cursor = db.cursor()
    result = None
    try:
        cursor.execute(query)
        db.commit()
        result = cursor.rowcount
        print('number of rows deleted', result)
        cursor.close()
        db.close()
        return result
    except Exception as err:
        cursor.close()
        db.close()
        print(f"Error: '{err}'")
