from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from dbEntity.devices.devices_entity import DeviceMPPTString 
from dbModel.device_mppt_string_model import DeviceMPPTStringModel 
from typing import Optional
class deviceMpptStringService:
    @staticmethod
    async def updateDeviceMPPTString(session: AsyncSession, current: float, id_device_list: int, namekey: str) -> Optional[DeviceMPPTStringModel]:
        try:
            query = (
                update(DeviceMPPTString)
                .where(DeviceMPPTString.id_device_list == id_device_list, DeviceMPPTString.namekey == namekey)
                .values(current=current)
            )
            await session.execute(query)
            await session.commit()

            updated_device = await session.execute(
                select(DeviceMPPTString).where(DeviceMPPTString.id_device_list == id_device_list, DeviceMPPTString.namekey == namekey)
            )
            device = updated_device.scalar_one_or_none()
            if device:
                return DeviceMPPTStringModel.from_orm(device)
            return None  
        except Exception as e:
            print("Error in updateDeviceMPPTString: ", e)
            await session.rollback()
            return None
        finally:
            await session.close()