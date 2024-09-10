# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert,delete, join, literal_column, select, text
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