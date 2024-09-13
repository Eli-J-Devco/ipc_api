# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text, update  # Thêm import cho update
from entity.devices.devices_entity import *

class deviceTypeService:
    @staticmethod
    async def selectTypeDeviceByID(session: AsyncSession, device_id: int):
        try:
            query = (
                select(DeviceType.name)
                .join(Devices, Devices.id_device_type == DeviceType.id)
                .where(Devices.id == device_id, Devices.status == 1)
            )
            result = await session.execute(query)  # Thực hiện câu lệnh truy vấn
            device_name = result.scalars().one_or_none()  # Lấy tên thiết bị hoặc None
            return device_name  # Trả về tên thiết bị (hoặc None nếu không tìm thấy)
        except Exception as e:
            print("Error in selectTypeDeviceByID: ", e)
            return None
        finally:
            await session.close()