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
    async def clone_last_mppt(self, session: AsyncSession,
                              id_template: int,
                              num_of_mppt: int):
        last_mppt = await self.get_mppt_point_formatted(id_template, session)
        last_mppt = last_mppt[-1] if last_mppt else None

        if not last_mppt:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Last MPPT not found")

        for _ in range(num_of_mppt):
            new_mppt_name = randint(1, 1000)
            new_mppt = PointMppt(**last_mppt.dict(exclude_unset=True, exclude={"id",
                                                                               "children",
                                                                               "name",
                                                                               "id_pointkey",
                                                                               "id_config_information",
                                                                               "parent", }),
                                 id_template=id_template,
                                 name=f"MPPT {new_mppt_name}",
                                 id_pointkey=f"MPPT{new_mppt_name}",
                                 id_config_information=PointType().MPPT_POINT,
                                 children=[])
            mppt_id = await self.add_point_mppt(id_template, new_mppt, session)
            new_mppt.id = mppt_id
            for string in last_mppt.children:
                new_string_name = randint(1, 1000)
                new_string = PointString(**string.dict(exclude_unset=True, exclude={"id",
                                                                                    "children",
                                                                                    "name",
                                                                                    "id_pointkey",
                                                                                    "id_config_information",
                                                                                    "parent", }),
                                         id_template=id_template,
                                         parent=mppt_id,
                                         name=f"String {new_string_name}",
                                         id_pointkey=f"String{new_string_name}",
                                         id_config_information=PointType().MPPT_STRING,
                                         children=[])
                string_id = await self.add_string_point(id_template, new_string, mppt_id, session)
                new_string.id = string_id
                for panel in string.children:
                    new_panel_name = randint(1, 1000)
                    new_panel = PointMpptBase(**panel.dict(exclude_unset=True, exclude={"id",
                                                                                        "children",
                                                                                        "name",
                                                                                        "id_pointkey",
                                                                                        "id_config_information",
                                                                                        "parent", }),
                                              id_template=id_template,
                                              parent=string_id,
                                              name=f"Panel {new_panel_name}",
                                              id_pointkey=f"Panel{new_panel_name}",
                                              id_config_information=PointType().MPPT_PANEL)
                    await self.add_panel_point(id_template, new_panel, string_id, session)
            await session.commit()
            session.expire_all()
        return await self.get_mppt_point_formatted(id_template, session)

    @async_db_request_handler
    async def add_mppt_point(self, session: AsyncSession, body: AddMPPTFilter):
        num_of_mppt = body.num_of_mppt
        num_of_strings = body.num_of_strings
        num_of_panels = body.num_of_panels

        if num_of_mppt < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Number of MPPTs must be at least 1")

        last_mppt = await self.get_last_mppt_point(body.id_template, body.is_clone_from_last, session)

        if num_of_strings < 1 and num_of_panels > 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Number of strings must be at least 1")

        for _ in range(num_of_mppt):
            new_mppt_name = randint(1, 1000)
            new_mppt = PointMppt(**last_mppt.dict(exclude_unset=True, exclude={"id",
                                                                               "children",
                                                                               "name",
                                                                               "id_pointkey",
                                                                               "id_config_information",
                                                                               "parent", }),
                                 id_template=body.id_template,
                                 name=f"MPPT {new_mppt_name}",
                                 id_pointkey=f"MPPT{new_mppt_name}",
                                 register_value=0,
                                 id_config_information=PointType().MPPT_POINT,
                                 children=[])
            mppt_id = await self.add_point_mppt(body.id_template, new_mppt, session)
            new_mppt.id = mppt_id
            await self.add_mppt_config(session, body.id_template, new_mppt)

            if num_of_strings > 0:
                result = await self.add_string(session,
                                               AddStringFilter(
                                                   id_template=body.id_template,
                                                   parent=mppt_id,
                                                   num_of_strings=num_of_strings,
                                                   num_of_panels=num_of_panels,
                                                   is_clone_from_last=body.is_clone_from_last,
                                               ),
                                               False,
                                               last_mppt.id)

                if isinstance(result, HTTPException):
                    raise result
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
            register_value=0,
            id_config_information=PointType().MPPT_CURRENT
        )
        mppt_voltage = PointMpptBase(
            id_template=id_template,
            parent=new_mppt.id,
            name=f"{new_mppt.name} Voltage",
            id_pointkey=f"{new_mppt.id_pointkey}Voltage",
            register_value=0,
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

            mppt_voltage = PointMpptBase(**mppt_voltage)
            mppt_current = PointMpptBase(**mppt_current)

        await self.add_panel_point(id_template, mppt_current, new_mppt.id, session)
        await self.add_panel_point(id_template, mppt_voltage, new_mppt.id, session)

    @async_db_request_handler
    async def add_string(self, session: AsyncSession,
                         body: AddStringFilter,
                         need_return: bool = True,
                         last_mppt_id: int = None):
        mppt_id = body.parent

        if mppt_id == 0:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent of point must be provided")

        num_of_strings = body.num_of_strings
        num_of_panels = body.num_of_panels

        if num_of_strings < 1:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Number of strings must be at least 1")

        last_string = await self.get_string_point(body.id_template, last_mppt_id, session)
        for __ in range(num_of_strings):
            new_string_name = randint(1, 1000)
            new_string = PointString(
                id_template=body.id_template,
                parent=mppt_id,
                name=f"String {new_string_name}",
                id_pointkey=f"String{new_string_name}",
                id_config_information=PointType().MPPT_STRING,
                children=[]
            )
            string_id = await self.add_string_point(body.id_template, new_string, mppt_id, session)
            if num_of_panels > 0:
                result = await self.add_panel(session,
                                              AddPanelFilter(
                                                  id_template=body.id_template,
                                                  parent=string_id,
                                                  num_of_panels=num_of_panels,
                                                  is_clone_from_last=body.is_clone_from_last
                                              ),
                                              False)

                if isinstance(result, HTTPException):
                    raise result

        if need_return:
            await session.commit()
            session.expire_all()
            return await self.get_mppt_point_formatted(body.id_template, session)

    @async_db_request_handler
    async def add_panel(self, session: AsyncSession,
                        body: AddPanelFilter,
                        need_return: bool = True,
                        last_string_id: int = None):
        string_id = body.parent

        if string_id == 0:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent of point must be provided")

        num_of_panels = body.num_of_panels

        if num_of_panels < 1:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Number of panels must be at least 1")

        for _ in range(num_of_panels):
            new_panel_name = randint(1, 1000)
            new_panel = PointMpptBase(id_template=body.id_template,
                                      parent=string_id,
                                      name=f"Panel {new_panel_name}",
                                      id_pointkey=f"Panel{new_panel_name}",
                                      id_config_information=PointType().MPPT_PANEL)
            await self.add_panel_point(body.id_template, new_panel, string_id, session)

        if need_return:
            await session.commit()
            session.expire_all()
            return await self.get_mppt_point_formatted(body.id_template, session)

    @async_db_request_handler
    async def get_number_of_point_by_type(self,
                                          id_template: int,
                                          id_config_information: int,
                                          parent: int | None,
                                          session: AsyncSession) -> int:
        query = (select(PointMpptEntity)
                 .where(PointMpptEntity.id_template == id_template)
                 .where(PointMpptEntity.id_config_information == id_config_information)
                 .where(PointMpptEntity.parent == parent)
                 .with_only_columns(func.count()))
        result = await session.execute(query)
        num_of_points = result.scalar()
        return num_of_points
