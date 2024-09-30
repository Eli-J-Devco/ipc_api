# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import platform
import sys

path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)

from dotenv import dotenv_values, find_dotenv, load_dotenv
from pydantic import BaseSettings
from async_db.config import MySqlConfigFactory, OrmProvider

if platform.system() == 'Linux':
    load_dotenv(find_dotenv(".env.production"))
else:
    load_dotenv(find_dotenv(".env.development"))

class Settings(BaseSettings):
    DATABASE_HOSTNAME: str
    DATABASE_PORT: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_USERNAME: str
    MQTT_USERNAME: str
    MQTT_PASSWORD: str
    MQTT_BROKER : str
    MQTT_PORT : int
    MQTT_TOPIC : str
Config = Settings()

db_config = MySqlConfigFactory(
    user=Config.DATABASE_USERNAME,
    password=Config.DATABASE_PASSWORD,
    host=Config.DATABASE_HOSTNAME,
    port=int(Config.DATABASE_PORT),
    db_name=Config.DATABASE_NAME,
)

orm_provider = OrmProvider(db_config)

# Tạo cấu hình kết nối DB mysql+aiomysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}
GetDBConfig = MySqlConfigFactory(
    user=Config.DATABASE_USERNAME,
    password=Config.DATABASE_PASSWORD,
    host=Config.DATABASE_HOSTNAME,
    port=int(Config.DATABASE_PORT),
    db_name=Config.DATABASE_NAME,
)

# quản lý kết nối và phiên làm việc (session) với cơ sở dữ liệu.
DBSessionManager = OrmProvider(GetDBConfig)