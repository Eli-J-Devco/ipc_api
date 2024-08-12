# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import platform
import sys

# from pathlib import Path
# from typing import Optional, Union, get_type_hints

path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.dirname(SCRIPT_DIR))
# print(f'SCRIPT_DIR: {SCRIPT_DIR}')
from dotenv import dotenv_values, find_dotenv, load_dotenv
from pydantic import BaseSettings

from async_db.config import MySqlConfigFactory, OrmProvider

# from pydantic import BaseModel
# from pydantic_settings import VERSION, BaseSettings, SettingsConfigDict




# print(f'{VERSION = }-202402')

# env_file = find_dotenv(f'.env.{os.getenv("ENV", "development")}')
# print(f'env_file: {env_file}')
# load_dotenv(env_file)
# load_dotenv(find_dotenv(".env"))
# test="dev"
# print(platform.system())
# load_dotenv(find_dotenv(".env.development"))
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
    FOLDER_PATH_LOG : str
    HEAD_FILE_LOG : str
    API_PORT : int
    PASSWORD_SECRET_KEY: str
    URL_SERVER_SYNC : str
    URL_SERVER_SYNC_FILE : str
    FTPSERVER_HOSTNAME : str
    FTPSERVER_PORT : int
    FTPSERVER_USERNAME : str
    FTPSERVER_PASSWORD : str
    MQTT_TOPIC_SUD_MODECONTROL_DEVICE : str
    MQTT_TOPIC_PUD_FEEDBACK_MODECONTROL : str
    MQTT_TOPIC_PUD_PROJECT_SETUP : str
    MQTT_TOPIC_PUD_CPU_SETUP : str
    MQTT_TOPIC_SUD_MODEGET_INFORMATION : str
    MQTT_TOPIC_SUD_MODEGET_CPU : str
    MQTT_TOPIC_SUD_CHOICES_MODE_AUTO_DETAIL : str
    MQTT_TOPIC_PUD_CHOICES_MODE_AUTO_DETAIL_FEEDBACK : str
    MQTT_TOPIC_SUD_CHOICES_MODE_AUTO : str
    MQTT_TOPIC_PUD_CHOICES_MODE_AUTO : str
    MQTT_TOPIC_SUD_DEVICES_ALL : str
    MQTT_TOPIC_SUD_FEEDBACK_CONTROL_MAN : str
    MQTT_TOPIC_SUD_FEEDBACK_CONTROL_MAN_SETUP : str
    MQTT_TOPIC_PUD_CONTROL_AUTO : str
    MQTT_TOPIC_SUD_SET_PROJECTSETUP_DATABASE : str
    MQTT_TOPIC_PUD_SET_PROJECTSETUP_DATABASE : str
    MQTT_TOPIC_PUD_LIST_DEVICE_PROCESS : str
    MQTT_TOPIC_PUD_MONIT_METER : str
    MQTT_TOPIC_SUD_SETTING_ARLAM : str
    MQTT_TOPIC_PUD_SETTING_ARLAM_FEEDBACK : str
    MQTT_TOPIC_SUD_MODIFY_DEVICE : str

Config = Settings()

db_config = MySqlConfigFactory(
    user=Config.DATABASE_USERNAME,
    password=Config.DATABASE_PASSWORD,
    host=Config.DATABASE_HOSTNAME,
    port=int(Config.DATABASE_PORT),
    db_name=Config.DATABASE_NAME,
)

orm_provider = OrmProvider(db_config)
