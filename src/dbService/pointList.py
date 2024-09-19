# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from dbEntity.project_setup.project_setup_entity import *
from dbEntity.pointList.point_list_entity import *
from dbEntity.devices.devices_entity import *
from dbModel.point_list_model import PointKeyModel 
import logging
logger = logging.getLogger(__name__)
class PointListService:
    @staticmethod
    async def select_point_keys_by_deviceid(session: AsyncSession, device_id: int):
        try:
            query = (
                select(Point.id_pointkey, ConfigInformation.namekey)
                .join(DevicePointMap, Point.id == DevicePointMap.id_point_list)
                .join(Devices, DevicePointMap.id_device_list == Devices.id)
                .join(ConfigInformation, ConfigInformation.id == Point.id_type_units)
                .where(
                    Devices.id == device_id,
                    DevicePointMap.status == 1,
                    Devices.id_template == Point.id_template
                )
            )
            result = await session.execute(query)
            points = result.mappings().all()
            return [PointKeyModel(id_pointkey=row["id_pointkey"], namekey=row["namekey"]) for row in points]  
        except Exception as e:
            logger.error("Error in queryPointKeysByDeviceId: ", e)
            return []
        finally:
            await session.close()