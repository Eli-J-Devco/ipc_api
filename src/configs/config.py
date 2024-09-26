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

# from pydantic_settings import VERSION, BaseSettings, SettingsConfigDict

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
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: str
    REFRESH_TOKEN_EXPIRE_MINUTES: str
    MQTT_USERNAME: str
    MQTT_PASSWORD: str
    MQTT_BROKER : str
    MQTT_PORT : int
    MQTT_TOPIC : str
    MQTT_USERNAME : str
    MQTT_PASSWORD : str
    API_DOCS_USERNAME : str
    API_DOCS_PASSWORD : str
    PATH_FILE_NETWORK_INTERFACE: str
    Path_File_Log : str
    Head_File_Log : str
    API_PORT : int
    PASSWORD_SECRET_KEY: str
    URL_SERVER_SYNC : str
    URL_SERVER_SYNC_FILE : str

class FolderSetting(BaseSettings):
    Path_File_Log : str
    Head_File_Log : str
    
class SyncSetting(BaseSettings):
    Name_Key_URL : str
    Name_Key_File_Log : str
    Name_Key_Ftp : str
    Number_File_Sync_Max : int
    ftpHost : str
    ftpPort : int
    ftpUname : str
    ftpPass : str
class MQTTSettings(BaseSettings):
    MQTT_USERNAME: str
    MQTT_PASSWORD: str
    MQTT_BROKER: str
    MQTT_PORT: int
    
class MQTTTopicSUD(BaseSettings):
    Control_Setup_Mode_Write: str
    Project_Get: str
    Control_Setup_Mode_Write_Detail: str
    Control_Setup_Auto: str
    Devices_All: str
    Devices_Detail: str
    Control_Feedback: str
    Control_Feedbacksetup: str
    Project_Set: str
    Control_Modify: str
    Control_Process : str

class MQTTTopicPUSH(BaseSettings):
    Control_Setup_Mode_Feedback: str
    Project_Information: str
    CPU_Information: str
    Control_Setup_Mode_Write_Detail_Feedback: str
    Control_Setup_Auto_Feedback: str
    Control_WriteAuto: str
    Project_Set_Feedback: str
    Control_Process: str
    Meter_Monitor: str
    Control_Setup_Mode_Write : str
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