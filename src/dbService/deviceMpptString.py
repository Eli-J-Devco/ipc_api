# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text, update
from entity.devices.devices_entity import *
class deviceMpptStringService:
    @staticmethod
    async def updateDeviceMPPTString(session: AsyncSession, current: float, id_device_list: int, namekey: str):
        try:
            query = (
                update(DeviceMPPTString)
                .where(DeviceMPPTString.id_device_list == id_device_list, DeviceMPPTString.namekey == namekey)
                .values(current=current)
            )
            await session.execute(query)
            await session.commit()
        except Exception as e:
            print("Error in updateDeviceMPPTString: ", e)
            await session.rollback()
        finally:
            await session.close()