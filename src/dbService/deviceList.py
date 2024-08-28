# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text, update  # Thêm import cho update
from entity.devicesBinh.deviceList import *

class deviceListService:
    @staticmethod
    async def selectAllDeviceList(session: AsyncSession):
        try:
            query = select(Devices)  # Tạo câu query Select All Bảng 
            result = await session.execute(query)  # Thực hiện câu lệnh truy vấn
            projects = result.scalars().all()  # Lấy tất cả các đối tượng ProjectSetup
            return [project.__dict__ for project in projects]  # Chuyển đổi thành dict 
        except Exception as e:
            print("Error in queryAllProjectSetup: ", e)
            return []
        finally:
            await session.close()

    @staticmethod
    async def selectDeviceListWhereName(session: AsyncSession, device_name: str):
        try:
            query = select(Devices).where(Devices.name == device_name)
            result = await session.execute(query)
            device = result.scalars().one_or_none()  # Lấy thiết bị hoặc None
            if device is None:
                return None  # Nếu không tìm thấy thiết bị
            # Chuyển đổi đối tượng thành dict và trả về
            return device.__dict__  # Trả về dict của đối tượng
        except Exception as e:
            print("Error in queryDeviceById: ", e)
            return None

    @staticmethod
    async def updateRatedPowerInID(session: AsyncSession, device_id: int, new_rated_power: float):
        try:
            # Tạo câu truy vấn để cập nhật rated_power
            query = (
                update(Devices)
                .where(Devices.id == device_id)
                .values(rated_power=new_rated_power)
            )
            result = await session.execute(query)  # Thực hiện câu lệnh cập nhật
            await session.commit()  # Cam kết thay đổi
            return result.rowcount  # Trả về số hàng đã cập nhật
        except Exception as e:
            print("Error in queryUpdateRatedPowerInID: ", e)
            return None
        finally:
            await session.close()
    @staticmethod
    async def updateDeviceModeByType(session: AsyncSession, mode: int):
        try:
            # Tạo câu truy vấn để cập nhật mode
            query = (
                update(Devices)
                .where(Devices.id_device_type == select(DeviceType.id).where(DeviceType.name == 'PV System Inverter').scalar_subquery())
                .values(mode=mode)
            )
            result = await session.execute(query)  # Thực hiện câu lệnh cập nhật
            await session.commit()  # Cam kết thay đổi
            print("data insert")
            return result.rowcount  # Trả về số hàng đã cập nhật
        except Exception as e:
            print("Error in updateDeviceModeByType: ", e)
            return None
        finally:
            await session.close()
    @staticmethod
    async def selectUniqueModesByDeviceType(session: AsyncSession):
        try:
            query = (
                select(Devices.mode, Devices.id)
                .join(DeviceType, Devices.id_device_type == DeviceType.id)
                .where(DeviceType.name == 'PV System Inverter', Devices.status == 1)
            )
            result = await session.execute(query)  # Thực hiện câu lệnh truy vấn
            modes = set(item['mode'] for item in result.mappings())  # Lấy các chế độ duy nhất
            return modes
        except Exception as e:
            print("Error in getUniqueModesByDeviceType: ", e)
            return None
        finally:
            await session.close()
