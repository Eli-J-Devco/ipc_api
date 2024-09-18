from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update,select
from entity.devices.devices_entity import DeviceMPPT 
from dbModel.device_mppt_model import DeviceMPPTModel
from typing import Optional
class deviceMpptService:
    @staticmethod
    async def updateDeviceMPPT(session: AsyncSession, voltage: float, current: float, id_device_list: int, namekey: str) -> Optional[DeviceMPPTModel]:
        try:
            query = (
                update(DeviceMPPT)
                .where(DeviceMPPT.id_device_list == id_device_list, DeviceMPPT.namekey == namekey)
                .values(voltage=voltage, current=current)
            )
            await session.execute(query)
            await session.commit()

            updated_device = await session.execute(
                select(DeviceMPPT).where(DeviceMPPT.id_device_list == id_device_list, DeviceMPPT.namekey == namekey)
            )
            device = updated_device.scalar_one_or_none()
            if device:
                return DeviceMPPTModel.from_orm(device) 
            return None 
        except Exception as e:
            print("Error in updateDeviceMPPT: ", e)
            await session.rollback()
            return None
        finally:
            await session.close()