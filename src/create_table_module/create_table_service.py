from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.schema import CreateTable
from sqlalchemy import MetaData, Table, Column

from .create_table_model import CreateTableModel


class TableColumn:
    def __init__(self, column_name: str, column_type):
        self.column_name = column_name
        self.column_type = column_type


class CreateTableRepository:
    @staticmethod
    def create_table(table_name: str, table_schema: List[TableColumn]):
        meta = MetaData()

        new_table = Table(table_name,
                          meta,
                          *CreateTableModel.default,)

        for column in table_schema:
            new_table.append_column(Column(column.column_name, column.column_type))

        return CreateTable(new_table)


class CreateTableService:
    def __init__(self, session: AsyncSession, table_repository: CreateTableRepository = CreateTableRepository()):
        self.table_repository = table_repository
        self.session = session

    async def create_table(self, table_name: str, table_schema: List[TableColumn]):
        await self.session.execute(self.table_repository.create_table(table_name, table_schema))
