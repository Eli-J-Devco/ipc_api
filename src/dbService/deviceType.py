from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from dbEntity.devices.devices_entity import DeviceType, Devices  # Import các mô hình Entity
from dbModel.device_type_model import DeviceTypeModel  # Import mô hình Pydantic
from typing import Optional
class deviceTypeService:
    @staticmethod
    async def selectTypeDeviceByID(session: AsyncSession, device_id: int) -> Optional[DeviceTypeModel]:
        try:
            query = (
                select(DeviceType.name)
                .join(Devices, Devices.id_device_type == DeviceType.id)
                .where(Devices.id == device_id, Devices.status == 1)
            )
            result = await session.execute(query)
            device_name = result.scalars().one_or_none()
            if device_name:
                return DeviceTypeModel(name=device_name)
            return None
        except Exception as e:
            print("Error in selectTypeDeviceByID: ", e)
            return None
        finally:
            await session.close()