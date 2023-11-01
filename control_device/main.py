import mysql.connector
from mysql.connector import Error
import pandas as pd

from ..backend_api import settings
print(settings.database_username)
# def create_server_connection(host_name, user_name, user_password, db_name):
#     connection = None
#     try:
#         connection = mysql.connector.connect(
#             host=host_name,
#             user=user_name,
#             passwd=user_password,
#             database=db_name
#         )
#         print("MySQL Database connection successful")
#     except Error as err:
#         print(f"Error: '{err}'")

#     return connection


# connection = create_server_connection("localhost", "root", "", "")
# q1 = """
# SELECT *
# FROM ;
# """
# results = read_query(connection, q1)
