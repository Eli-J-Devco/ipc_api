# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/

import sys
import time

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils import path_directory_relative

# Describe functions before writing code
# /**
# 	 * @description path directory relative
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {project_name}
# 	 * @return data (path of project)
# 	 */
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

# Describe functions before writing code
# /**
# 	 * @description connect database
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {user_id}
# 	 * @return data ()
# 	 */
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

