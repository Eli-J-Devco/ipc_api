import asyncio

from .config import OrmProvider
from .create_table_service import CreateTableService


class CreateTableModule:
    def __init__(self, db_config: OrmProvider):
        self.db_config = db_config
        self.service = CreateTableService(asyncio.run(db_config.get_db()), db_config.Base.metadata)

    async def set_up(self):
        await self.db_config.create_all()

    async def drop_all(self):
        await self.db_config.drop_all()

    async def reflect_table(self):
        await self.db_config.reflect_table()
