# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text, update  # Thêm import cho update
from entity.devices.devices_entity import *
from entity.upload_channel.upload_channel_entity import *
class deviceListService:
    @staticmethod
    async def selectAllDeviceList(session: AsyncSession):
        try:
            query = select(Devices)
            result = await session.execute(query)
            projects = result.scalars().all()
            return [project.__dict__ for project in projects] 
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
            device = result.scalars().one_or_none()
            if device is None:
                return None
            return device.__dict__ 
        except Exception as e:
            print("Error in queryDeviceById: ", e)
            return None

    @staticmethod
    async def updateRatedPowerInID(session: AsyncSession, device_id: int, new_rated_power: float):
        try:
            query = (
                update(Devices)
                .where(Devices.id == device_id)
                .values(rated_power=new_rated_power)
            )
            result = await session.execute(query)
            await session.commit()
            return result.rowcount
        except Exception as e:
            print("Error in queryUpdateRatedPowerInID: ", e)
            await session.rollback()
            return None
        finally:
            await session.close()
    @staticmethod
    async def updateDeviceModeByType(session: AsyncSession, mode: int):
        try:
            query = (
                update(Devices)
                .where(Devices.id_device_type == select(DeviceType.id).where(DeviceType.name == 'PV System Inverter').scalar_subquery())
                .values(mode=mode)
            )
            result = await session.execute(query)
            await session.commit()
            return result.rowcount
        except Exception as e:
            print("Error in updateDeviceModeByType: ", e)
            await session.rollback()
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
            result = await session.execute(query)
            modes = set(item['mode'] for item in result.mappings())
            return modes
        except Exception as e:
            print("Error in getUniqueModesByDeviceType: ", e)
            return None
        finally:
            await session.close()
    @staticmethod
    async def selectDevicesByUploadChannelID(session: AsyncSession, upload_channel_id: int):
        try:
            query = (
                select(Devices.id, Devices.name, Devices.rtu_bus_address)
                .join(UploadChannelDeviceMap, Devices.id == UploadChannelDeviceMap.id_device)
                .where(Devices.status == 1, UploadChannelDeviceMap.id_upload_channel == upload_channel_id)
            )
            result = await session.execute(query)
            devices = result.mappings().all()
            return [dict(device) for device in devices]
        except Exception as e:
            print("Error in selectDevicesByUploadChannel: ", e)
            return []
        finally:
            await session.close()
