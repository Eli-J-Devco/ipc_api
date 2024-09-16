# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text, update  # Thêm import cho update
from entity.devices.devices_entity import *

class deviceMpptService:
    @staticmethod
    async def updateDeviceMPPT(session: AsyncSession, voltage: float, current: float, id_device_list: int, namekey: str):
        try:
            query = (
                update(DeviceMPPT)
                .where(DeviceMPPT.id_device_list == id_device_list, DeviceMPPT.namekey == namekey)
                .values(voltage=voltage, current=current)
            )
            await session.execute(query)
            await session.commit()
        except Exception as e:
            print("Error in updateDeviceMPPT: ", e)
            await session.rollback()
        finally:
            await session.close()