# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert,delete,update, join, literal_column, select, text
from entity.sync_data.sync_data_entity import *

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
            print("Sync data successfully --->")
            return result.rowcount  
        except Exception as e:
            print(f"Error: '{e}'")
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
            print("Deleted synced data successfully --->")
            return result.rowcount
        except Exception as e:
            print(f"Error: '{e}'")
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
                .limit(limit)  # Sử dụng biến limit
            )
            result = await session.execute(query)
            sync_data_list = result.scalars().all()  # Lấy danh sách bản ghi

            # Trả về danh sách các bản ghi dưới dạng danh sách từ điển
            return [
                {key: value for key, value in record.__dict__.items() if key != '_sa_instance_state'}
                for record in sync_data_list
            ]
        except Exception as e:
            print("Error in select_sync_data: ", e)
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
            await session.commit()  # Commit thay đổi
            print("Deleted synced data successfully --->")
            return result.rowcount  # Trả về số lượng bản ghi đã xóa
        except Exception as e:
            print("Error in delete_sync_data: ", e)
            await session.rollback()  # Rollback nếu có lỗi
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
            await session.commit()  # Commit thay đổi
        except Exception as e:
            print("Error in update_error_status: ", e)
            await session.rollback()  # Rollback nếu có lỗi
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
            await session.commit()  # Commit thay đổi
        except Exception as e:
            print("Error in update_number_of_time_retry: ", e)
            await session.rollback()  # Rollback nếu có lỗi
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
            remaining_files = result.scalar()  # Lấy giá trị đầu tiên
            return remaining_files
        except Exception as e:
            print("Error in count_remaining_files: ", e)
            return None
        finally:
            await session.close()

