import os
from dotenv import load_dotenv
from pathlib import Path

from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Config(BaseSettings):
    MQTT_HOST: str = 'localhost'
    MQTT_PORT: int = 1883
    MQTT_USERNAME: str = ''
    MQTT_PASSWORD: str = ''
    MQTT_CLIENT_ID: str = 'client_id'
    MQTT_TOPIC: str = 'topic'
    MQTT_QOS: int = 0

    MYSQL_HOST: str = 'localhost'
    MYSQL_DB_NAME: str = 'database'
    MYSQL_USER: str = 'root'
    MYSQL_PASSWORD: str = 'password'
    MYSQL_PORT: int = 3306

    SETUP_URL: str = "localhost:8000"
    SETUP_AUTH_ENDPOINT: str = "/authentication/login/"
    SETUP_DEVICES_ENDPOINT: str = "/devices/get/all/"
    SETUP_POINTS_ENDPOINT: str = "/point/get/all/"
    SETUP_USERNAME: str = "admin"
    SETUP_PASSWORD: str = "admin"
    PASSWORD_SECRET_KEY: str = "password_secret_key"


config = Config()
