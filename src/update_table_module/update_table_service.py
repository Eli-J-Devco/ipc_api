import logging
from typing import List

from sqlalchemy import MetaData, select, text, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .update_table_model import Point
from ..async_db.src.async_db.wrapper import async_db_request_handler
from ..create_table_module.create_table_model import CreateTableModel
from ..devices_entity import (Devices as DevicesEntity,
                              PointList as PointListEntity,
                              DeviceMppt as DeviceMpptEntity,
                              DeviceMpptString as DeviceMpptStringEntity, DevicePanel, )
from ..devices_model import (DeviceModel,
                             PointType,
                             DeviceMppt, PointMPPT, PointString)

logger = logging.getLogger(__name__)


class UpdateTableService:
    def __init__(self,
                 metadata: MetaData):
        self.metadata = metadata

    @async_db_request_handler
    async def update_table(self, device: DeviceModel, session: AsyncSession):
        query = f"SELECT * FROM {device.table_name} LIMIT 1"
        result = await session.execute(text(query))

        default_points = list(CreateTableModel.default.keys())
        points = result.keys()
        points = [point for point in points if point not in default_points]

        device_points = [point.id_pointkey for point in device.points]
        new_points = [point for point in device.points if point.id_pointkey not in points]
        delete_points = [point for point in points if point not in device_points]

        if new_points:
            for point in new_points:
                query = (f"ALTER TABLE {device.table_name} "
                         f"ADD COLUMN {point.id_pointkey} FLOAT AFTER {default_points[-1]};"
                         if point.id_config_information == PointType.POINT.value
                         else f"ALTER TABLE {device.table_name} "
                              f"ADD COLUMN {point.id_pointkey} FLOAT;")
                query = query + (f"INSERT INTO device_point_list_map (id_device_list, id_point_list, name) "
                                 f"VALUES ({device.id}, {point.id}, '{point.name}');")

                await session.execute(text(query))
                logging.info(f"Added new point {point} to {device.table_name}")

        if delete_points:
            for point in delete_points:
                query = f"ALTER TABLE {device.table_name} DROP COLUMN {point}"
                await session.execute(text(query))
                logging.info(f"Deleted point {point} from {device.table_name}")

        mppt_points = []
        for point in device.points:
            if (point.id_config_information not in
                    [PointType.MPPT.value, PointType.STRING.value, PointType.PANEL.value]):
                continue
            if point.id_config_information == PointType.MPPT.value:
                mppt = PointMPPT(**point.dict())

                for string in device.points:
                    if string.id_config_information == PointType.STRING.value and string.parent == point.id:
                        new_string = PointString(**string.dict())
                        for panel in device.points:
                            if panel.id_config_information == PointType.PANEL.value and panel.parent == string.id:
                                new_string.children.append(Point(**panel.dict()))
                        mppt.children.append(new_string)
                mppt_points.append(mppt)

        result = await self.update_device_mppt(device.id, mppt_points, session)
        if isinstance(result, Exception):
            return result

    @async_db_request_handler
    async def update_device_mppt(self, device_id: int,
                                 mppts: list[PointMPPT],
                                 session: AsyncSession):
        for mppt in mppts:
            query = (select(DeviceMpptEntity)
                     .where(DeviceMpptEntity.id_device_list == device_id)
                     .where(DeviceMpptEntity.id_point_list == mppt.id))
            result = await session.execute(query)
            mppt_entity = result.scalars().first()

            new_mppt = mppt_entity
            if not mppt_entity:
                new_mppt = DeviceMpptEntity(id_device_list=device_id,
                                            id_point_list=mppt.id,
                                            name=mppt.name,
                                            namekey=mppt.id_pointkey)
                session.add(new_mppt)
                await session.flush()

            if mppt.children:
                for string in mppt.children:
                    query = (select(DeviceMpptStringEntity)
                             .where(DeviceMpptStringEntity.id_device_list == device_id)
                             .where(DeviceMpptStringEntity.id_point_list == string.id))
                    result = await session.execute(query)
                    string_entity = result.scalars().first()

                    new_string = string_entity
                    if not string_entity:
                        new_string = DeviceMpptStringEntity(id_device_list=device_id,
                                                            id_point_list=string.id,
                                                            id_device_mppt=new_mppt.id,
                                                            name=string.name,
                                                            namekey=string.id_pointkey)
                        session.add(new_string)
                        await session.flush()

                    if string.children:
                        for panel in string.children:
                            query = (select(DevicePanel)
                                     .where(DevicePanel.id_device_list == device_id)
                                     .where(DevicePanel.id_point_list == panel.id))
                            result = await session.execute(query)
                            panel_entity = result.scalars().first()

                            if not panel_entity:
                                new_panel = DevicePanel(id_device_list=device_id,
                                                        id_point_list=panel.id,
                                                        id_device_string=new_string.id,
                                                        name=panel.name)
                                session.add(new_panel)
                                await session.flush()
