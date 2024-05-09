from dotenv import load_dotenv
from pydantic import BaseSettings

from .async_db.src.async_db.config import MySqlConfigFactory, OrmProvider

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
    MQTT_RETAIN: bool = True

    DATABASE_HOSTNAME: str = 'localhost'
    DATABASE_PORT: int = 3306
    DATABASE_PASSWORD: str = 'admin'
    DATABASE_NAME: str = 'root'
    DATABASE_USERNAME: str = 'nextwave_db'

    PM2_MQTT_HOST: str
    PM2_MQTT_PORT: str
    PM2_MQTT_TOPIC: str
    PM2_MQTT_USERNAME: str
    PM2_MQTT_PASSWORD: str
    PM2_MQTT_CLIENT_ID: str
    PM2_MQTT_QOS: str
    PM2_MQTT_RETAIN: str


config = Config()

if config.PM2_MQTT_USERNAME == '':
    config.PM2_MQTT_USERNAME = None
if config.PM2_MQTT_PASSWORD == '':
    config.PM2_MQTT_PASSWORD = None
if config.MQTT_USERNAME == '':
    config.MQTT_USERNAME = None
if config.MQTT_PASSWORD == '':
    config.MQTT_PASSWORD = None

db_config = MySqlConfigFactory(
    user=config.DATABASE_USERNAME,
    password=config.DATABASE_PASSWORD,
    host=config.DATABASE_HOSTNAME,
    port=int(config.DATABASE_PORT),
    db_name=config.DATABASE_NAME,
)

orm_provider = OrmProvider(db_config)
