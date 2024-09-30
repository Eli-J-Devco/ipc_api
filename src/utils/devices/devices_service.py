from dataclasses import asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text
from async_db.wrapper import async_db_request_handler
from src.utils.devices.devices_model import DeviceInitOutput,DeviceInit,DeviceFull
from src.utils.devices.devices_entity import Devices as DevicesEntity
from src.configs.query_sql.device import query_all as device_query

class DeviceService:
    def __init__(self,session: AsyncSession, **kwargs
                    ):
        self.session=session
    @async_db_request_handler
    async def get_device(self, id_device: int):
        try:
            query =device_query.select_only_device_use_driver.format(id_device=id_device)
            result = await self.session.execute(text(query))
            device = result.first()
            # print(f'device: {device}')
            if not device:
                return 
            device=device._asdict()
        except Exception as e:
            print("Error get_devices: ", e)
            return 
        finally:
            await self.session.close()
            return DeviceFull(**dict(device))        
    @async_db_request_handler
    async def get_devices(self):
        try:
            query =device_query.select_all_device
            result = await self.session.execute(text(query))
            devices = [row._asdict() for row in result.all()]
            if not devices:
                return []
            device_list=[]
            for device in devices:
                device_list.append(DeviceInit(**device))
        except Exception as e:
            print("Error get_devices: ", e)
            return []
        finally:
            await self.session.close()
            return device_list
    @async_db_request_handler
    async def classify_devices(self):
        try:
            devices=await self.get_devices()
            if not devices:
                pass
            device_list=[]
            for device in devices:
                if device.type==0:
                    device_list.append(DeviceInit(**device.dict()))
        except Exception as e:
            print("Error get_devices: ", e)
        finally:
            return DeviceInitOutput(devices=device_list)
    