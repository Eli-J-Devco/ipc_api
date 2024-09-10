# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text, update  # Thêm import cho update
from entity.devicesBinh.deviceList import *

class deviceMpptService:
    @staticmethod
    async def updateDeviceMPPT(session: AsyncSession, voltage: float, current: float, id_device_list: int, namekey: str):
        try:
            query = (
                update(DeviceMPPT)
                .where(DeviceMPPT.id_device_list == id_device_list, DeviceMPPT.namekey == namekey)
                .values(voltage=voltage, current=current)
            )
            await session.execute(query)  # Thực hiện câu lệnh cập nhật
            await session.commit()  # Cam kết thay đổi
        except Exception as e:
            print("Error in updateDeviceMPPT: ", e)
            await session.rollback()  # Hoàn tác nếu có lỗi
        finally:
            await session.close()