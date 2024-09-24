# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import sys
import time

import mysql.connector

path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")+"/"
sys.path.append(path)
from configs.config import Config

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

# def insert_data_table_device(data):
#     db = create_server_connection(Config.DATABASE_HOSTNAME, Config.DATABASE_PORT, Config.DATABASE_USERNAME, Config.DATABASE_PASSWORD, Config.DATABASE_NAME)
#     if db:
#         cursor = db.cursor(dictionary=True)
#         try:
#             for entry in data:
#                 sql = entry['sql']
#                 values = entry['values']
#                 cursor.executemany(sql, values)
#             db.commit()
#             print("Data inserted successfully.")
#         except Exception as e:
#             print(f"Error during data insertion: {e}")
#             db.rollback()
#         finally:
#             cursor.close()
#             db.close()
def insert_data_table_device(data):
    db = create_server_connection(Config.DATABASE_HOSTNAME, Config.DATABASE_PORT, Config.DATABASE_USERNAME, Config.DATABASE_PASSWORD, Config.DATABASE_NAME)
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


