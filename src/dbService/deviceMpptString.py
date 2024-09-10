# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text, update  # Thêm import cho update
from entity.devicesBinh.deviceList import *
class deviceMpptStringService:
    @staticmethod
    async def updateDeviceMPPTString(session: AsyncSession, current: float, id_device_list: int, namekey: str):
        try:
            query = (
                update(DeviceMPPTString)
                .where(DeviceMPPTString.id_device_list == id_device_list, DeviceMPPTString.namekey == namekey)
                .values(current=current)
            )
            await session.execute(query)  # Thực hiện câu lệnh cập nhật
            await session.commit()  # Cam kết thay đổi
        except Exception as e:
            print("Error in updateDeviceMPPTString: ", e)
            await session.rollback()  # Hoàn tác nếu có lỗi
        finally:
            await session.close()