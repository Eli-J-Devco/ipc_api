import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.schema import CreateTable
from sqlalchemy import MetaData, Table, Column, select, text, ForeignKey

from .create_table_entity import Devices, PointList
from .create_table_model import CreateTableModel
from ..create_devices_model import Point, DeviceModel

logger = logging.getLogger(__name__)

class TableColumn:
    def __init__(self, column_name: str, column_type):
        self.column_name = column_name
        self.column_type = column_type


class CreateTableRepository:
    @staticmethod
    def create_table(table_name: str, table_schema: List[TableColumn], meta: MetaData):
        try:
            logging.info(f"Creating table {table_name}")
            is_table = meta.tables.__dict__.get(table_name)
            if is_table:
                logging.info(f"Table {table_name} already exists")
                raise Exception(f"Table {table_name} already exists")

            default_columns_config = CreateTableModel.default
            default_columns = [Column(name=default_columns_config[col].name,
                                      type_=default_columns_config[col].col_type,
                                      nullable=default_columns_config[col].nullable,
                                      primary_key=default_columns_config[col].primary_key,
                                      *[ForeignKey(default_columns_config[col].foreign_key["name"],
                                                   ondelete=default_columns_config[col].foreign_key["ondelete"],
                                                   onupdate=default_columns_config[col].foreign_key["onupdate"])]
                                      if default_columns_config[col].foreign_key else []
                                      ) for col in default_columns_config]
            new_table = Table(table_name,
                              meta,
                              *default_columns,
                              extend_existing=True)

            for column in table_schema:
                new_table.append_column(Column(column.column_name, column.column_type), replace_existing=True)

            new_table = CreateTable(new_table, if_not_exists=True)
            del default_columns
            return new_table
        except Exception as e:
            logging.error(f"Error when creating {table_name}: {e}")
            raise e


class CreateTableService:
    def __init__(self,
                 metadata: MetaData,
                 table_repository: CreateTableRepository = CreateTableRepository()):
        self.table_repository = table_repository
        self.metadata = metadata

    async def create_table(self, table_name: str, table_schema: List[TableColumn], session: AsyncSession):
        try:
            query = str(self.table_repository.create_table(table_name, table_schema, self.metadata)).replace('"', '')
            await session.execute(text(query))
            await session.commit()
            logging.info(f"Table {table_name} created")
        except Exception as e:
            logging.error(f"Error when creating table {table_name}: {e}")
            await session.rollback()
            raise e
        finally:
            await session.close()

    async def delete_table(self, table_name: str, session: AsyncSession):
        try:
            query = f"DROP TABLE IF EXISTS {table_name}"
            await session.execute(text(query))
            await session.commit()
            logging.info(f"Table {table_name} deleted")
        except Exception as e:
            logging.error(f"Error when deleting table {table_name}: {e}")
            await session.rollback()
            raise e
        finally:
            logger.info("Closing session")
            await session.close()

    @staticmethod
    async def get_devices(session: AsyncSession) -> List[DeviceModel]:
        try:
            query = select(Devices)
            result = await session.execute(query)
            devices = result.scalars().all()
            return [DeviceModel(**device.__dict__) for device in devices]
        except Exception as e:
            logging.error(e)
            raise e
        finally:
            logger.info("Closing session")
            await session.close()

    @staticmethod
    async def get_points(id_template: int, session: AsyncSession) -> List[Point]:
        try:
            query = select(PointList).where(PointList.id_template == id_template).where(PointList.status == 1)
            result = await session.execute(query)
            points = result.scalars().all()
            return [Point(**point.__dict__) for point in points]
        except Exception as e:
            logging.error(e)
            raise e
        finally:
            logger.info("Closing session")
            await session.close()
