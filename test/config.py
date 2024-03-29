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

print(f'{VERSION = }')

# load_dotenv()
# load_dotenv(dotenv_path=Path(".env"))
# load_dotenv(find_dotenv(".env"))
# test="dev"
if platform.system() == 'Linux':
    load_dotenv(find_dotenv(".env.production"))
else:
    load_dotenv(find_dotenv(".env.development"))
    
# class AppConfigError(Exception):
#     pass

# def _parse_bool(val: Union[str, bool]) -> bool:  # pylint: disable=E1136
#     return val if type(val) == bool else val.lower() in ['true', 'yes', '1']

# # AppConfig class with required fields, default values, type checking, and typecasting for int and bool values

# class AppConfig:
#     DATABASE_HOSTNAME: str
#     DATABASE_PORT: str
#     DATABASE_PASSWORD: str
#     DATABASE_NAME: str
#     DATABASE_USERNAME: str
#     SECRET_KEY: str
#     REFRESH_SECRET_KEY: str
#     ALGORITHM: str
#     ACCESS_TOKEN_EXPIRE_MINUTES: int
#     REFRESH_TOKEN_EXPIRE_MINUTES: int
#     MQTT_USERNAME: str
#     MQTT_PASSWORD: str
#     MQTT_BROKER : str
#     MQTT_PORT : int
#     MQTT_TOPIC : str
#     MQTT_USERNAME : str
#     MQTT_PASSWORD : str
#     API_DOCS_USERNAME : str
#     API_DOCS_PASSWORD : str
#     PATH_FILE_NETWORK_INTERFACE: str
#     FOLDER_PATH_LOG : str
#     HEAD_FILE_LOG : str

#     def __init__(self, env):
#         for field in self.__annotations__:
#             if not field.isupper():
#                 continue

#             # Raise AppConfigError if required field not supplied
#             default_value = getattr(self, field, None)
#             if default_value is None and env.get(field) is None:
#                 raise AppConfigError('The {} field is required'.format(field))

#             # Cast env var value to expected type and raise AppConfigError on failure
#             try:
#                 var_type = get_type_hints(AppConfig)[field]
#                 if var_type == bool:
#                     value = _parse_bool(env.get(field, default_value))
#                 else:
#                     value = var_type(env.get(field, default_value))

#                 self.__setattr__(field, value)
#             except ValueError:
#                 raise AppConfigError('Unable to cast value of "{}" to type "{}" for "{}" field'.format(
#                     env[field],
#                     var_type,
#                     field
#                 )
#                 )

#     def __repr__(self):
#         return str(self.__dict__)


# # Expose Config object for app to import
# Config = AppConfig(os.environ)

# Config = {
#     **dotenv_values(".env.development"),  # load shared development variables
#     **dotenv_values(".env.production"),  # load production variables
#     # **os.environ,  # override loaded values with environment variables
# }
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
Config = Settings()

# 