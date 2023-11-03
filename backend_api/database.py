# from config import *
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# sys.path.insert(1, "D:/NEXTWAVE/project/ipc_api")


load_dotenv(dotenv_path=Path("../.env"))
database_hostname = os.getenv('DATABASE_HOSTNAME')
database_port = os.getenv('DATABASE_PORT')
database_password = os.getenv('DATABASE_PASSWORD')
database_name = os.getenv('DATABASE_NAME')
database_username = os.getenv('DATABASE_USERNAME')

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
