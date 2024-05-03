from .config import OrmProvider


class CreateTableModule:
    def __init__(self, db_config: OrmProvider):
        self.db_config = db_config

    async def set_up(self):
        await self.db_config.create_all()

    async def drop_all(self):
        await self.db_config.drop_all()
