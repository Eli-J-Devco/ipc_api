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



async def MySQL_Selectv1(query):
    db = create_server_connection(
        DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)

    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        print(result)
        cursor.close()
        db.close()
        return result
    except Exception as err:
        cursor.close()
        db.close()
        print(f"Error: '{err}'")
        
def MySQL_Select(query,val):
    db = create_server_connection(
    DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)

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
            
def MySQL_Insertv1(query,val):
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
            
def MySQL_Insertv2(table_name,lenval,val):
    db = create_server_connection(
    DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)

    cursor = db.cursor(dictionary=True)
    # cursor = db.cursor()
    result = None
    try:
        # Tạo danh sách các cột
        columns = ['time', 'id_device','id_upload_channel']
        for i in range(len(lenval)):
            columns.append(f'pt{i}')

        # Tạo câu truy vấn
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
        # cursor.execute(query,(val,))
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
        print("Record Updated successfully ")
        cursor.close()
        db.close()
        return result
    except Exception as err:
        cursor.close()
        db.close()
        print(f"Error: '{err}'")


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
