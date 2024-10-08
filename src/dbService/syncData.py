# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert,delete,update, join, literal_column, select, text
from dbEntity.sync_data.sync_data_entity import *
from dbModel.sync_data_model import SyncDataModel 
import logging
logger = logging.getLogger(__name__)
class SyncDataService:
    @staticmethod
    async def insert_sync_data(session: AsyncSession, data_list: list):
        try:
            records = [
                {
                    'id': entry[0],  
                    'id_device': entry[1],
                    'modbusdevice': entry[2],
                    'ensuredir': entry[3],
                    'source': entry[4],
                    'filename': entry[5],
                    'createtime': entry[6],
                    'data': entry[7],  
                    'id_upload_channel': entry[8]  
                }
                for entry in data_list
            ]
            query = insert(SyncData).values(records)
            result = await session.execute(query)
            await session.commit()
            logger.info("Sync data successfully --->")
            return result.rowcount  
        except Exception as e:
            logger.error(f"Error: '{e}'")
            await session.rollback() 
            return None
        finally:
            await session.close()
    @staticmethod
    async def delete_synced_data(session: AsyncSession):
        try:
            query = delete(SyncData).where(SyncData.synced == 1)
            result = await session.execute(query)
            await session.commit()
            logger.info("Deleted synced data successfully --->")
            return result.rowcount
        except Exception as e:
            logger.error(f"Error: '{e}'")
            await session.rollback()
            return None
        finally:
            await session.close()
    @staticmethod
    async def select_number_row_send_cloud(session: AsyncSession, id_upload_channel: int, id_device: int, limit: int ):
        try:
            query = (
                select(SyncData)
                .where(
                    SyncData.id_upload_channel == id_upload_channel,
                    SyncData.synced == 0,
                    SyncData.updatetime.is_(None),
                    SyncData.error.is_(None),
                    SyncData.id_device == id_device
                )
                .order_by(SyncData.id.asc())
                .limit(limit)
            )
            result = await session.execute(query)
            sync_data_list = result.scalars().all()

            return [
                SyncDataModel(**{
                    "id": record.id,
                    "id_device": record.id_device,
                    "modbusdevice": record.modbusdevice,
                    "ensuredir": record.ensuredir,
                    "source": record.source,
                    "filename": record.filename,
                    "createtime": record.createtime,
                    "data": record.data,
                    "id_upload_channel": record.id_upload_channel,
                    "synced": record.synced,
                    "updatetime": record.updatetime,
                    "error": record.error,
                    "number_of_time_retry": record.number_of_time_retry,
                })
                for record in sync_data_list
            ]
        except Exception as e:
            logger.error("Error in select_sync_data: ", e)
            return None
        finally:
            await session.close()
    @staticmethod
    async def delete_synced_data(session: AsyncSession, id: str, id_upload_channel: int, id_device: int):
        try:
            query = (
                delete(SyncData)
                .where(
                    SyncData.id == id,
                    SyncData.id_upload_channel == id_upload_channel,
                    SyncData.id_device == id_device
                )
            )
            result = await session.execute(query)
            await session.commit()
            logger.info("Deleted synced data successfully --->")
            return result.rowcount
        except Exception as e:
            logger.error("Error in delete_sync_data: ", e)
            await session.rollback()
            return None
        finally:
            await session.close()
    @staticmethod
    async def update_error_status(session: AsyncSession, id: datetime, id_upload_channel: int, id_device: int):
        try:
            query = (
                update(SyncData)
                .where(
                    SyncData.id == id,
                    SyncData.id_upload_channel == id_upload_channel,
                    SyncData.id_device == id_device
                )
                .values(error=1)
            )
            await session.execute(query)
            await session.commit()
        except Exception as e:
            logger.error("Error in update_error_status: ", e)
            await session.rollback()
        finally:
            await session.close()
    @staticmethod
    async def update_number_of_time_retry(session: AsyncSession, number_of_time_retry: int, id: datetime, id_upload_channel: int, id_device: int):
        try:
            query = (
                update(SyncData)
                .where(
                    SyncData.id == id,
                    SyncData.id_upload_channel == id_upload_channel,
                    SyncData.id_device == id_device
                )
                .values(number_of_time_retry=number_of_time_retry)
            )
            await session.execute(query)
            await session.commit()
        except Exception as e:
            logger.error("Error in update_number_of_time_retry: ", e)
            await session.rollback()
        finally:
            await session.close()
    @staticmethod
    async def count_remaining_files(session: AsyncSession, id_upload_channel: int):
        try:
            query = (
                select(func.count().label("remaining_files"))
                .select_from(SyncData)
                .where(
                    SyncData.synced == 0,
                    SyncData.error.is_(None),
                    SyncData.id_upload_channel == id_upload_channel
                )
            )
            result = await session.execute(query)
            remaining_files = result.scalar()
            return remaining_files
        except Exception as e:
            logger.error("Error in count_remaining_files: ", e)
            return None
        finally:
            await session.close()
    @staticmethod
    async def update_number_of_time_retry(session: AsyncSession, id: int, id_upload_channel: int, id_device: int):
        try:
            query = select(SyncData.number_of_time_retry).where(
                SyncData.id == id,
                SyncData.id_upload_channel == id_upload_channel,
                SyncData.id_device == id_device
            )
            result = await session.execute(query)
            current_retry_value = result.scalar_one_or_none()

            if current_retry_value is not None:
                new_retry_value = current_retry_value + 1

                update_query = (
                    update(SyncData)
                    .where(
                        SyncData.id == id,
                        SyncData.id_upload_channel == id_upload_channel,
                        SyncData.id_device == id_device
                    )
                    .values(number_of_time_retry=new_retry_value)
                )
                update_result = await session.execute(update_query)
                await session.commit()  

                return new_retry_value  
            return current_retry_value
        except Exception as e:
            logger.error("Error in update_number_of_time_retry: ", e)
            return None
        finally:
            await session.close()