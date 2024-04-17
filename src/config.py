from functools import reduce
import secrets

from nest.core.database.orm_provider import AsyncOrmProvider
from pydantic import BaseSettings

from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    MYSQL_HOST: str
    MYSQL_PORT: str
    MYSQL_PASSWORD: str
    MYSQL_DB_NAME: str
    MYSQL_USER: str
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_VALUE: str
    ACCESS_TOKEN_EXPIRE_UNIT: str
    REFRESH_TOKEN_EXPIRE_VALUE: str
    REFRESH_TOKEN_EXPIRE_UNIT: str
    MQTT_USERNAME: str
    MQTT_PASSWORD: str
    MQTT_BROKER: str
    MQTT_PORT: int
    MQTT_TOPIC: str
    MQTT_USERNAME: str
    MQTT_PASSWORD: str
    API_DOCS_USERNAME: str
    API_DOCS_PASSWORD: str
    PATH_FILE_NETWORK_SAMPLE: str
    PATH_FILE_NETWORK_INTERFACE: str
    FOLDER_PATH_LOG: str
    HEAD_FILE_LOG: str
    API_PORT: int
    PASSWORD_SECRET_KEY: str
    URL_SERVER_SYNC: str
    URL_SERVER_SYNC_FILE: str
    FTPSERVER_HOSTNAME: str
    FTPSERVER_PORT: int
    FTPSERVER_USERNAME: str
    FTPSERVER_PASSWORD: str


env_config = Settings()

config = AsyncOrmProvider(
    db_type="mysql",
    config_params=dict(
        host=env_config.MYSQL_HOST,
        db_name=env_config.MYSQL_DB_NAME,
        user=env_config.MYSQL_USER,
        password=env_config.MYSQL_PASSWORD,
        port=int(env_config.MYSQL_PORT),
    )
)
