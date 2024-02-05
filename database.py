import os
import sys
from datetime import datetime

from sqlalchemy import (DOUBLE, BigInteger, Boolean, Column, DateTime,
                        ForeignKey, Integer, String, Text, create_engine)
from sqlalchemy.orm import (declarative_base, mapped_column, relationship,
                            sessionmaker)
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from config import Config
from libcom import path_directory_relative

path=path_directory_relative("ipc_api") # name of project
sys.path.append(path)
# 
database_hostname =Config.DATABASE_HOSTNAME
database_port = Config.DATABASE_PORT
database_password =Config.DATABASE_PASSWORD
database_name =Config.DATABASE_NAME
database_username =Config.DATABASE_USERNAME
print(f'database_hostname: {database_hostname}')
print(f'database_port: {database_port}')
print(f'database_password: {database_password}')
print(f'database_name: {database_name}')
print(f'database_username: {database_username}')
SQLALCHEMY_DATABASE_URL = f'mysql+pymysql://{database_username}:{database_password}@{database_hostname}:{database_port}/{database_name}'
# ?allowMultiQueries=true&charset=utf8mb4
# SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:12345@localhost:3307/test'

engine = create_engine(SQLALCHEMY_DATABASE_URL,   isolation_level="READ UNCOMMITTED")#, echo=True
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