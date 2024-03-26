import asyncio
import os
import sys
# path=path_directory_relative("ipc_api") # name of project
# sys.path.append(path)
# #
from contextlib import asynccontextmanager
from datetime import datetime

import pymysql
import pymysql.cursors
import sqlalchemy as sa
from pymysql.constants import CLIENT
from sqlalchemy import (DOUBLE, BigInteger, Boolean, Column, DateTime,
                        ForeignKey, Integer, String, Text, create_engine)
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
# from sqlalchemy.orm import (declarative_base, mapped_column, relationship,
#                             sessionmaker)
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (DeclarativeBase, declarative_base, mapped_column,
                            relationship, sessionmaker)
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
# -------------------------------------------------------------------------------------
SQLALCHEMY_DATABASE_URL = f'mysql+pymysql://{database_username}:{database_password}@{database_hostname}:{database_port}/{database_name}'
engine = create_engine(SQLALCHEMY_DATABASE_URL,   
                       isolation_level="READ UNCOMMITTED",
                       pool_size=20, 
                       max_overflow=100,
                       )
# 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# @asynccontextmanager
def get_db():
    db = SessionLocal()
    try:
        return db
    except Exception as err:
            db.rollback()
    finally:
        db.close()
# class Base(DeclarativeBase):
#     pass
# SQLALCHEMY_DATABASE_URL = f'mysql+aiomysql://{database_username}:{database_password}@{database_hostname}:{database_port}/{database_name}'
# engine = create_async_engine(SQLALCHEMY_DATABASE_URL
#                             #  ,connect_args={"check_same_thread":False}
#                        )
# SessionLocal = async_sessionmaker(engine)
# # Base = declarative_base()
# async def get_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     db = SessionLocal()
#     try:
#         yield db
#     except Exception as err:
#             await db.rollback()
#     finally:
#         await db.close()

