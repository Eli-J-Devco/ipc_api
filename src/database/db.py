import os
import sys
from datetime import datetime

# path=path_directory_relative("ipc_api") # name of project
# sys.path.append(path)
# #
import pymysql
import pymysql.cursors
import sqlalchemy as sa
from pymysql.constants import CLIENT
from sqlalchemy import (DOUBLE, BigInteger, Boolean, Column, DateTime,
                        ForeignKey, Integer, String, Text, create_engine)
from sqlalchemy.orm import (declarative_base, mapped_column, relationship,
                            sessionmaker)
from sqlalchemy.pool import QueuePool
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from configs.config import Config

# from libcom import path_directory_relative

database_hostname =Config.DATABASE_HOSTNAME
database_port = Config.DATABASE_PORT
database_password =Config.DATABASE_PASSWORD
database_name =Config.DATABASE_NAME
database_username =Config.DATABASE_USERNAME
# print(f'database_hostname: {database_hostname}')
# print(f'database_port: {database_port}')
# print(f'database_password: {database_password}')
# print(f'database_name: {database_name}')
# print(f'database_username: {database_username}')
SQLALCHEMY_DATABASE_URL = f'mysql+pymysql://{database_username}:{database_password}@{database_hostname}:{database_port}/{database_name}'



engine = create_engine(SQLALCHEMY_DATABASE_URL,   
                       isolation_level="READ UNCOMMITTED",
                       pool_size=20, 
                       max_overflow=100,
                       )
# def get_pymysql_connection():
#     return pymysql.connect(
#         host=database_hostname,
#         port=int(database_port),
#         user=database_username,
#         password=database_password,
#         database=database_name,
#         client_flag=CLIENT.MULTI_STATEMENTS,
#          charset='utf8mb4',
#          max_allowed_packet=16 * 1024 * 1024,
#          connect_timeout=10,
#         #   client_flag=0,
#         # cursorclass=pymysql.cursors.DictCursor
#     )
# engine = sa.create_engine("mysql+pymysql://", creator=get_pymysql_connection)
# 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# db = SessionLocal()
def get_db():
    db = SessionLocal()
    try:
        return db
    except Exception as err:
            db.rollback()
    finally:
        db.close()