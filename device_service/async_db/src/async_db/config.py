import enum
from abc import abstractmethod
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


class DbTypes(enum.Enum):
    POSTGRES = "postgres"
    MYSQL = "mysql"


class ConfigFactoryBase:
    def __init__(self,
                 user: str,
                 password: str,
                 host: str,
                 port: int,
                 db_name: str,
                 db_type: str):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.db_name = db_name

    @abstractmethod
    def get_config(self):
        pass


class PostgresConfigFactory(ConfigFactoryBase):
    def get_config(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"


class MySqlConfigFactory(ConfigFactoryBase):
    def get_config(self):
        return f"mysql+aiomysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"


class Base(DeclarativeBase):
    pass


class OrmProvider:
    def __init__(self, db_config: ConfigFactoryBase):
        self.Base = Base
        self.config = db_config.get_config()
        self.engine = create_async_engine(self.config)
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def create_all(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.create_all)

    async def drop_all(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.drop_all)

    async def reflect_table(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.reflect)

    async def get_db(self) -> AsyncSession:
        db = self.session()
        try:
            return db
        finally:
            await db.close()

    @asynccontextmanager
    async def session(self) -> AsyncSession:
        db = self.session()
        try:
            yield db
        finally:
            await db.close()
