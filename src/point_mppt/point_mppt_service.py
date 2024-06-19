# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import logging
from abc import abstractmethod

from fastapi import HTTPException, status
from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler
from sqlalchemy.ext.asyncio import AsyncSession

from .point_mppt_entity import PointMppt as PointMpptEntity
from .point_mppt_filter import AddMPPTFilter, AddStringFilter, AddPanelFilter
from .point_mppt_model import PointMppt, PointMpptBase, PointString
from ..config import env_config
from ..devices.devices_service import DevicesService
from ..point.point_model import PointBase
from ..point_config.point_config_filter import PointType
from ..utils.utils import generate_id


@Injectable
class PointMpptService:
    @abstractmethod
    async def add_point_mppt(self, id_template: int, point_mppt: PointMppt, session: AsyncSession) -> int:
        """
        Abstract method to add point mppt
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param point_mppt:
        :param session:
        :return: int
        """
        pass

    @abstractmethod
    async def add_string_point(self, id_template: int, point_string: PointString, id_point_mppt: int,
                               session: AsyncSession) -> int:
        """
        Abstract method to add string point
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param point_string:
        :param id_point_mppt:
        :param session:
        :return: int
        """
        pass

    @abstractmethod
    async def add_panel_point(self, id_template: int, point_panel: PointBase, id_point_string: int,
                              session: AsyncSession) -> int:
        """
        Abstract method to add panel point
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param point_panel:
        :param id_point_string:
        :param session:
        :return: int
        """
        pass

    @abstractmethod
    async def get_mppt_point(self, id_template: int, session: AsyncSession) -> list[dict]:
        """
        Abstract method to get mppt point
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param session:
        :return: list[dict]
        """
        pass

    @abstractmethod
    async def get_mppt_config_point(self, id_template: int,
                                    id_point_mppt: int, session: AsyncSession) -> list[dict]:
        """
        Abstract method to get mppt config point
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param id_point_mppt:
        :param session:
        :return: list[dict]
        """
        pass

    @abstractmethod
    async def get_string_point(self, id_template: int,
                               id_point_mppt: int, session: AsyncSession) -> list[dict]:
        """
        Abstract method to get string point
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param id_point_mppt:
        :param session:
        :return: list[dict]
        """
        pass

    @abstractmethod
    async def get_panel_point(self, id_template: int,
                              id_point_string: int, session: AsyncSession) -> list[dict]:
        """
        Abstract method to get panel point
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param id_point_string:
        :param session:
        :return: list[dict]
        """
        pass

    @abstractmethod
    async def get_last_panel_point(self, id_template: int,
                                   id_point_string: int,
                                   is_clone: bool,
                                   session: AsyncSession) -> PointMpptBase:
        """
        Abstract method to get last panel point
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param id_point_string:
        :param is_clone:
        :param session:
        :return: PointMpptBase
        """
        pass

    @abstractmethod
    async def get_last_string_formatted(self, id_template: int, parent: int, session: AsyncSession) -> PointString:
        """
        Abstract method to get last string formatted
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param parent:
        :param session:
        :return: PointString
        """
        pass

    @async_db_request_handler
    async def get_mppt_point_formatted(self, id_template: int, session: AsyncSession) -> list[PointMppt] | list[PointString]:
        """
        Get mppt point formatted
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param session:
        :return: list[PointMppt]
        """
        point_mppt = await self.get_mppt_point(id_template, session)

        response = []
        for point in point_mppt:
            adding_children = PointMppt(**point, children=[])
            adding_children.register_value = point["register"]

            config_points = await self.get_mppt_config_point(id_template, adding_children.id, session)
            for config_point in config_points:
                adding_children.children.append(PointMpptBase(**config_point))

            string_points = await self.get_string_point(id_template, adding_children.id, session)
            for string_point in string_points:
                adding_string_children = PointString(**string_point, children=[])

                panel_points = await self.get_panel_point(id_template, adding_string_children.id, session)
                for panel_point in panel_points:
                    adding_string_children.children.append(PointMpptBase(**panel_point))
                adding_children.children.append(adding_string_children)
            response.append(adding_children)
        return response

    @async_db_request_handler
    async def get_string_point_formatted(self, id_template: int, session: AsyncSession) -> list[PointString]:
        """
        Get mppt point formatted
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param session:
        :return: list[PointString]
        """
        point_string = await self.get_string_point(id_template, 0, session)
        response = []
        for point in point_string:
            adding_children = PointString(**point, children=[])
            adding_children.register_value = point["register"]

            panel_points = await self.get_panel_point(id_template, adding_children.id, session)
            for panel_point in panel_points:
                adding_children.children.append(PointMpptBase(**panel_point))
            response.append(adding_children)
        return response

    @staticmethod
    def convert_point(point: PointMppt | PointString | PointMpptBase,
                      body: AddMPPTFilter | AddStringFilter | AddPanelFilter,
                      point_type: str, parent: int = None) -> PointMpptEntity:
        """
        Convert point to PointMpptEntity
        :author: nhan.tran
        :date: 20-05-2024
        :param point:
        :param body:
        :param point_type:
        :param parent:
        :return: PointMpptEntity
        """
        new_point = PointMpptEntity(**PointBase(**point.dict(exclude_unset=True))
                                    .dict(exclude={"id", "children", "register_value"}))
        new_point.name = f"New {point_type}"
        new_point.id_pointkey = f"{point_type}{generate_id(env_config.DEFAULT_ID_LENGTH)}"
        new_point.parent = parent if parent and parent > 0 else None
        new_point.register = point.register_value if point.register_value else 0
        new_point.id_template = body.id_template

        return new_point

    @async_db_request_handler
    async def add_mppt_point(self, session: AsyncSession, body: AddMPPTFilter) -> list[PointMppt]:
        """
        Add mppt point to database
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :param body:
        :return: list[PointMppt]
        """
        num_of_mppt = body.num_of_mppt
        num_of_strings = body.num_of_strings
        is_last = True

        if num_of_mppt < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Number of MPPTs must be at least 1")

        mppt = None
        if body.is_clone_from_last:
            mppt_list = await self.get_mppt_point_formatted(body.id_template, session)
            mppt = mppt_list[-1] if mppt_list else None

        if not mppt:
            mppt = PointMppt(id_config_information=PointType().MPPT_POINT, )
            is_last = False
        body.is_clone_from_last = is_last

        for _ in range(num_of_mppt):
            add_mppt = self.convert_point(mppt, body, "MPPT")
            session.add(add_mppt)
            await session.flush()
            await self.add_mppt_config(session, body.id_template, add_mppt, is_last, mppt.id)

            if mppt.children:
                for string in mppt.children:
                    if string.id_config_information != PointType().MPPT_STRING:
                        continue
                    add_string = self.convert_point(string, body, "String", add_mppt.id)
                    session.add(add_string)
                    await session.flush()

                    if string.children:
                        for panel in string.children:
                            add_panel = self.convert_point(panel, body, "Panel", add_string.id)
                            session.add(add_panel)
                            await session.flush()
            elif num_of_strings > 0:
                await self.add_string(session,
                                      body=AddStringFilter(id_template=body.id_template,
                                                           parent=add_mppt.id,
                                                           is_clone_from_last=is_last,
                                                           num_of_strings=num_of_strings,
                                                           num_of_panels=body.num_of_panels),
                                      need_return=False,
                                      last_mppt_id=mppt.id, )
        await session.commit()
        session.expire_all()
        await DevicesService().update_device_points(body.id_template, session)
        return await self.get_mppt_point_formatted(body.id_template, session)

    @async_db_request_handler
    async def add_mppt_config(self, session: AsyncSession,
                              id_template: int,
                              new_mppt: PointMppt,
                              is_clone: bool = False,
                              last_mppt_id: int = None) -> None:
        """
        Add mppt config to database
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :param id_template:
        :param new_mppt:
        :param is_clone:
        :param last_mppt_id:
        :return: None
        """
        mppt_current = PointBase(
            id_template=id_template,
            parent=new_mppt.id,
            name=f"{new_mppt.name} Current",
            id_pointkey=f"{new_mppt.id_pointkey}Current",
            id_config_information=PointType().MPPT_CURRENT
        )
        mppt_voltage = PointBase(
            id_template=id_template,
            parent=new_mppt.id,
            name=f"{new_mppt.name} Voltage",
            id_pointkey=f"{new_mppt.id_pointkey}Voltage",
            id_config_information=PointType().MPPT_VOLTAGE
        )

        if is_clone:
            mppt_voltage, mppt_current = await self.get_mppt_config_point(id_template, last_mppt_id, session)

            mppt_voltage["parent"] = new_mppt.id
            mppt_voltage["name"] = f"{new_mppt.name} Voltage"
            mppt_voltage["id_pointkey"] = f"{new_mppt.id_pointkey}Voltage"

            mppt_current["parent"] = new_mppt.id
            mppt_current["name"] = f"{new_mppt.name} Current"
            mppt_current["id_pointkey"] = f"{new_mppt.id_pointkey}Current"

            mppt_voltage = PointBase(**mppt_voltage)
            mppt_current = PointBase(**mppt_current)

        await self.add_panel_point(id_template, mppt_current, new_mppt.id, session)
        await self.add_panel_point(id_template, mppt_voltage, new_mppt.id, session)

    @async_db_request_handler
    async def add_string(self, session: AsyncSession,
                         body: AddStringFilter,
                         need_return: bool = True,
                         last_mppt_id: int = None) -> list[PointMppt] | list[PointString]:
        """
        Add string to database
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :param body:
        :param need_return:
        :param last_mppt_id:
        :return: list[PointMppt]
        """
        num_of_strings = body.num_of_strings
        num_of_panels = body.num_of_panels
        is_last = True
        if num_of_strings < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Number of strings must be at least 1")

        string = None
        if body.is_clone_from_last:
            string = await self.get_last_string_formatted(body.id_template, last_mppt_id, session)

        if not string:
            string = PointString(id_config_information=PointType().MPPT_STRING,
                                 parent=last_mppt_id if last_mppt_id and last_mppt_id > 0 else None)
            is_last = False

        body.is_clone_from_last = is_last
        for _ in range(num_of_strings):
            add_string = self.convert_point(string, body, "String", last_mppt_id)
            session.add(add_string)
            await session.flush()

            if string.children:
                for panel in string.children:
                    add_panel = self.convert_point(panel, body, "Panel", add_string.id)
                    session.add(add_panel)
                    await session.flush()
            elif num_of_panels > 0:
                await self.add_panel(session,
                                     body=AddPanelFilter(id_template=body.id_template,
                                                         parent=add_string.id,
                                                         is_clone_from_last=is_last,
                                                         num_of_panels=num_of_panels),
                                     need_return=False,
                                     last_string_id=string.id)

        if need_return:
            await session.commit()
            session.expire_all()
            await DevicesService().update_device_points(body.id_template, session)
            if body.is_string_only:
                return await self.get_string_point_formatted(body.id_template, session)
            return await self.get_mppt_point_formatted(body.id_template, session)

    @async_db_request_handler
    async def add_panel(self, session: AsyncSession,
                        body: AddPanelFilter,
                        need_return: bool = True,
                        last_string_id: int = None) -> list[PointMppt] | list[PointString]:
        """
        Add panel to database
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :param body:
        :param need_return:
        :param last_string_id:
        :return: list[PointMppt]
        """
        num_of_panels = body.num_of_panels
        is_last = True

        if num_of_panels < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Number of panels must be at least 1")

        panel = None
        if body.is_clone_from_last:
            panel = await self.get_last_panel_point(body.id_template, last_string_id, True, session)

        if not panel:
            panel = PointMpptBase(id_config_information=PointType().MPPT_PANEL,
                                  parent=body.parent,
                                  id_pointtype=279)
            is_last = False
        body.is_clone_from_last = is_last
        for _ in range(num_of_panels):
            add_panel = self.convert_point(panel, body, "Panel", body.parent)
            session.add(add_panel)
            await session.flush()

        if need_return:
            await session.commit()
            session.expire_all()
            await DevicesService().update_device_points(body.id_template, session)
            if body.is_string_only:
                return await self.get_string_point_formatted(body.id_template, session)
            return await self.get_mppt_point_formatted(body.id_template, session)
