# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import platform
import sys
from pathlib import Path
from typing import Optional, Union, get_type_hints

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from dotenv import dotenv_values, find_dotenv, load_dotenv
# from pydantic import BaseModel
from pydantic_settings import VERSION, BaseSettings, SettingsConfigDict

print(f'{VERSION = }-2024')
# load_dotenv()
# load_dotenv(dotenv_path=Path(".env"))
# load_dotenv(find_dotenv(".env"))
# test="dev"
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
Config = Settings()