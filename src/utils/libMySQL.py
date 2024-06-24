# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import sys
import time

# import asyncio
# import threading
import mysql.connector

# import pandas as pd
# from mysql.connector import Error

# import mybatis_mapper2sql
# sys.path.append((lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
#                 ("src"))
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")+"/"
sys.path.append(path)
from configs.config import Config

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
    retry_count = 0
    max_retries = 3
    while retry_count < max_retries:
        try:
            connection = mysql.connector.connect(
                host=host_name,
                port=port_name,
                user=user_name,
                passwd=user_password,
                database=db_name,
            )
            return connection
        except Exception as err:
            print(f"Error Connecting: '{err}'")
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying connection in 1 seconds...")
                time.sleep(1)
            else:
                print(f"Unable to connect to the database")
                return None

async def MySQL_Select_v1(query):
    db = create_server_connection(
        DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            db.close()
            return result
        except Exception as err:
            cursor.close()
            db.close()
            print(f"Error: '{err}'")
            return None
    else:
        return None

def MySQL_Select(query, val):
    db = create_server_connection(
        DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(query, val)
            result = cursor.fetchall()
            cursor.close()
            db.close()
            return result
        except Exception as err:
            cursor.close()
            db.close()
            print(f"Error: '{err}'")
            return None
    else:
        return None

def MySQL_Insert(query):
    db = create_server_connection(
        DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    if db:
        cursor = db.cursor(dictionary=True)
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
            return None
    else:
        return None

def MySQL_Insert_v1(query, val):
    db = create_server_connection(
        DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(query, val)
            db.commit()
            result = cursor.rowcount
            cursor.close()
            db.close()
            return result
        except Exception as err:
            cursor.close()
            db.close()
            print(f"Error: '{err}'")
            return None
    else:
        return None

def MySQL_Insert_v2(table_name, len_val, val):
    db = create_server_connection(
        DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    if db:
        cursor = db.cursor()
        try:
            columns = ['time', 'id_device'] + [f'pt{i}' for i in range(len(len_val))]
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
            cursor.execute(query, val)
            db.commit()
            result = cursor.rowcount
            cursor.close()
            db.close()
            return result
        except Exception as err:
            cursor.close()
            db.close()
            print(f"Error: '{err}'")
            return None
    else:
        return None

def MySQL_Insert_v3(data):
    db = create_server_connection(DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            for key, value in data.items():
                sql = value[0]
                val = value[1]
                cursor.execute(sql, val)
            db.commit()
            result = cursor.rowcount
            cursor.close()
            db.close()
            return result
        except Exception as err:
            cursor.close()
            db.close()
            print(f"Error: '{err}{val}'")
            return None
    else:
        return None

def MySQL_Insert_v4(query, val):
    db = create_server_connection(
        DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            cursor.executemany(query, val)
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
            return None
    else:
        return None

def MySQL_Insert_v5(query, val):
    db = create_server_connection(DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(query, val)
            print("Data inserted successfully")
            db.commit()
            result = cursor.rowcount
            cursor.close()
            db.close()
            return result
        except Exception as err:
            cursor.close()
            db.close()
            print(f"Error: '{err} {val}'")
            return None
    else:
        return None

def MySQL_Update(query):
    db = create_server_connection(
        DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            db.commit()
            result = cursor.rowcount
            cursor.close()
            db.close()
            return result
        except Exception as err:
            cursor.close()
            db.close()
            print(f"Error: '{err}'")
            return None
    else:
        return None

def MySQL_Update_V1(query, val):
    db = create_server_connection(
        DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(query, val)
            result = cursor.fetchall()
            db.commit()
            result = cursor.rowcount
            cursor.close()
            db.close()
            return result
        except Exception as err:
            cursor.close()
            db.close()
            print(f"Error: '{err}'")
            return None
    else:
        return None

def MySQL_Update_v2(query, val):
    db = create_server_connection(
        DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    if db:
        cursor = db.cursor(dictionary=True)
        try:
            cursor.executemany(query, val)
            db.commit()
            result = cursor.rowcount
            cursor.close()
            db.close()
            return result
        except Exception as err:
            cursor.close()
            db.close()
            print(f"Error: '{err}'")
            return None
    else:
        return None

def MySQL_Delete(query):
    db = create_server_connection(
        DATABASE_HOSTNAME, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
    if db:
        cursor = db.cursor(dictionary=True)
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
            return None
    else:
        return None
