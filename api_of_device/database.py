# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
# from config import *
# import os
# sys.path.insert(1, "D:/NEXTWAVE/project/ipc_api")
import sys
import time

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils import path_directory_relative

# from pathlib import Path


path=path_directory_relative("ipc_api") # name of project
sys.path.append(path)
from config import Config

database_hostname = Config.DATABASE_HOSTNAME
database_port = Config.DATABASE_PORT
database_password = Config.DATABASE_PASSWORD
database_name = Config.DATABASE_NAME
database_username = Config.DATABASE_USERNAME

SQLALCHEMY_DATABASE_URL = f'mysql+pymysql://{database_username}:{database_password}@{database_hostname}:{database_port}/{database_name}'
# SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:12345@localhost:3307/test'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
