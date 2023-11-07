# from config import *
# import os
# sys.path.insert(1, "D:/NEXTWAVE/project/ipc_api")
import sys
import time

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# from pathlib import Path


sys.path.insert(1, "../")
from config import Config

# load_dotenv(dotenv_path=Path("../.env"))
# database_hostname = os.getenv('DATABASE_HOSTNAME')
# database_port = os.getenv('DATABASE_PORT')
# database_password = os.getenv('DATABASE_PASSWORD')
# database_name = os.getenv('DATABASE_NAME')
# database_username = os.getenv('DATABASE_USERNAME')

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
