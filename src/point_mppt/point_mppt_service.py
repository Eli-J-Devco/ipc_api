import logging
from abc import abstractmethod
from random import randint

from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable
from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from .point_mppt_filter import AddMPPTFilter, AddStringFilter, AddPanelFilter
from .point_mppt_model import PointMppt, PointMpptBase, PointString
from .point_mppt_entity import PointMppt as PointMpptEntity, ManualPointMppt as ManualPointMpptEntity

from ..point_config.point_config_filter import PointType


@Injectable
class PointMpptService:
    @abstractmethod
    async def add_point_mppt(self, id_template: int, point_mppt: PointMppt, session: AsyncSession) -> int:
        pass

    @abstractmethod
    async def add_string_point(self, id_template: int, point_string: PointString, id_point_mppt: int,
                               session: AsyncSession) -> int:
        pass

    @abstractmethod
    async def add_panel_point(self, id_template: int, point_panel: PointMpptBase, id_point_string: int,
                              session: AsyncSession):
        pass

    @abstractmethod
    async def get_mppt_point(self, id_template: int, session: AsyncSession):
        pass

    @abstractmethod
    async def get_mppt_config_point(self, id_template: int, id_point_mppt: int, session: AsyncSession):
        pass

    @abstractmethod
    async def get_string_point(self, id_template: int, id_point_mppt: int, session: AsyncSession):
        pass

    @abstractmethod
    async def get_panel_point(self, id_template: int, id_point_string: int, session: AsyncSession):
        pass

    @abstractmethod
    async def get_last_mppt_point(self, id_template: int, is_clone: bool, session: AsyncSession) -> PointMppt:
        pass

    @abstractmethod
    async def get_last_string_point(self, id_template: int,
                                    id_point_mppt: int,
                                    is_clone: bool,
                                    session: AsyncSession) -> PointString:
        pass

    @abstractmethod
    async def get_last_panel_point(self, id_template: int,
                                   id_point_string: int,
                                   is_clone: bool,
                                   session: AsyncSession) -> PointMpptBase:
        pass

    @async_db_request_handler
    async def get_mppt_point_formatted(self, id_template: int, session: AsyncSession) -> list[PointMppt]:
        point_mppt = await self.get_mppt_point(id_template, session)
        response = []
        for point in point_mppt:
            adding_children = PointMppt(**point, children=[])

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
    async def add_mppt_point(self, session: AsyncSession, body: AddMPPTFilter):
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
            mppt = PointMppt(id=0,
                             id_config_information=PointType().MPPT_POINT, )
            is_last = False
        body.is_clone_from_last = is_last
        for _ in range(num_of_mppt):
            add_mppt = PointMpptEntity(**mppt.dict(exclude={"id", "children", "register_value"}))
            add_mppt.name = f"MPPT {_ + 1 + mppt.id}"
            add_mppt.id_pointkey = f"MPPT{_ + 1 + mppt.id}"
            add_mppt.register = mppt.register_value if mppt.register_value else 0
            add_mppt.id_template = body.id_template
            session.add(add_mppt)
            await session.flush()
            await self.add_mppt_config(session, body.id_template, add_mppt, is_last, mppt.id)

            if mppt.children:
                for string in mppt.children:
                    add_string = PointMpptEntity(**string.dict(exclude={"id",
                                                                        "children",
                                                                        "register_value",
                                                                        "parent"}),
                                                 register=string.register_value if string.register_value else 0,
                                                 parent=add_mppt.id,
                                                 id_template=body.id_template)
                    session.add(add_string)
                    await session.flush()

                    if string.children:
                        for panel in string.children:
                            add_panel = PointMpptEntity(**panel.dict(exclude={"id",
                                                                              "children",
                                                                              "register_value",
                                                                              "parent"}),
                                                        register=panel.register_value if panel.register_value else 0,
                                                        parent=add_string.id,
                                                        id_template=body.id_template)
                            session.add(add_panel)
                            await session.flush()
            elif num_of_strings > 0:
                await self.add_string(session, body, add_mppt, False, mppt.id)
        await session.commit()
        session.expire_all()
        return await self.get_mppt_point_formatted(body.id_template, session)

    @async_db_request_handler
    async def add_mppt_config(self, session: AsyncSession,
                              id_template: int,
                              new_mppt: PointMppt,
                              is_clone: bool = False,
                              last_mppt_id: int = None):
        mppt_current = PointMpptBase(
            id_template=id_template,
            parent=new_mppt.id,
            name=f"{new_mppt.name} Current",
            id_pointkey=f"{new_mppt.id_pointkey}Current",
            id_config_information=PointType().MPPT_CURRENT
        )
        mppt_voltage = PointMpptBase(
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

            logging.info("=====================================")
            logging.info(f"mppt_voltage: {mppt_current}")
            logging.info("=====================================")
            mppt_voltage = PointMppt(**mppt_voltage)
            mppt_current = PointMppt(**mppt_current)

        await self.add_panel_point(id_template, mppt_current, new_mppt.id, session)
        await self.add_panel_point(id_template, mppt_voltage, new_mppt.id, session)

    @async_db_request_handler
    async def add_string(self, session: AsyncSession,
                         body: AddStringFilter,
                         new_mppt: PointMppt,
                         need_return: bool = True,
                         last_mppt_id: int = None):
        num_of_strings = body.num_of_strings
        num_of_panels = body.num_of_panels
        is_last = True

        if num_of_strings < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Number of strings must be at least 1")

        string = None
        if body.is_clone_from_last:
            string_list = await self.get_mppt_point_formatted(body.id_template, session)
            for exist_string in string_list:
                if exist_string.id == last_mppt_id and exist_string.id_config_information == PointType().MPPT_STRING:
                    string = exist_string
                    break

        if not string:
            string = PointString(id=0,
                                 id_config_information=PointType().MPPT_STRING,
                                 parent=new_mppt.id)
            is_last = False
        body.is_clone_from_last = is_last
        for _ in range(num_of_strings):
            add_string = PointMpptEntity(**string.dict(exclude={"id", "children", "register_value"}))
            add_string.name = f"String {_ + 1 + string.id}"
            add_string.id_pointkey = f"String{_ + 1 + string.id}"
            add_string.register = string.register_value if string.register_value else 0
            add_string.id_template = body.id_template
            session.add(add_string)
            await session.flush()

            if string.children:
                for panel in string.children:
                    add_panel = PointMpptEntity(**panel.dict(exclude={"id", "children", "register_value"}),
                                                register=panel.register_value if panel.register_value else 0,
                                                parent=add_string.id)
                    session.add(add_panel)
                    await session.flush()
            elif num_of_panels > 0:
                await self.add_panel(session, body, add_string, False, string.id)

        if need_return:
            await session.commit()
            session.expire_all()
            return await self.get_mppt_point_formatted(body.id_template, session)

    @async_db_request_handler
    async def add_panel(self, session: AsyncSession,
                        body: AddPanelFilter,
                        new_string: PointString,
                        need_return: bool = True,
                        last_string_id: int = None):
        num_of_panels = body.num_of_panels
        is_last = True

        if num_of_panels < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Number of panels must be at least 1")

        panel = None
        if body.is_clone_from_last:
            panel = await self.get_last_panel_point(body.id_template, last_string_id, True, session)

        if not panel:
            panel = PointMpptBase(id=0,
                                  id_config_information=PointType().MPPT_PANEL,
                                  parent=new_string.id)
            is_last = False
        body.is_clone_from_last = is_last
        for _ in range(num_of_panels):
            add_panel = PointMpptBase(**panel.dict(exclude={"id", "register_value"}))
            add_panel.name = f"Panel {_ + 1 + panel.id}"
            add_panel.id_pointkey = f"Panel{_ + 1 + panel.id}"
            add_panel.register = panel.register_value if panel.register_value else 0
            add_panel.id_template = body.id_template
            session.add(add_panel)
            await session.flush()

        if need_return:
            await session.commit()
            session.expire_all()
            return await self.get_mppt_point_formatted(body.id_template, session)
