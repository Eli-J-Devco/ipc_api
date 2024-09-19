# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
# import json
# from uuid import uuid1

# import mqttools
from sqlalchemy import select, update
from sqlalchemy.sql import func, insert, join, literal_column, select, text

# from async_db.wrapper import async_db_request_handler
from configs.config import orm_provider as db_config
from dbEntity.devices.devices_entity import Devices as DevicesEntity

# from utils.mqttManager import gzip_decompress


class DeviceService:
    # def __init__(self):
    #     pass
    async def update_device(self,payload):
        try:
            if 'CODE' in payload.keys() and 'PAYLOAD' in payload.keys():
                if payload['CODE']=="UpdateDev":
                    id_device=payload['PAYLOAD']['id']      
                    query = (select(DevicesEntity)
                                .where(DevicesEntity.id == id_device))
                    db_new=await db_config.get_db()
                    result=await db_new.execute(query)
                    await db_new.commit()
                    output = result.scalars().first()
                    if output:
                        return {
                            "rated_power": output.rated_power,
                            "rated_power_custom":output.rated_power_custom,
                            "min_watt_in_percent":output.min_watt_in_percent,
                            "maximum_DC_input_current":output.DC_voltage,
                            "rated_DC_input_voltage":output.DC_current,
                            "efficiency":output.efficiency
                            }
        except Exception as e:
            print("Error update_device: ", e)
        finally:
            await db_new.close()