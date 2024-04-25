import logging
from abc import abstractmethod

from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .point_mppt_model import PointMppt, PointMpptBase, PointString
from .point_mppt_entity import PointMppt as PointMpptEntity, ManualPointMppt as ManualPointMpptEntity

from ..point_config.point_config_filter import PointType


@Injectable
class PointMpptService:
    @abstractmethod
    async def add_point_mppt(self, id_template: int, point_mppt: PointMppt, session: AsyncSession) -> int:
        pass

    @abstractmethod
    async def add_string_point(self, id_template: int, point_string: PointString, id_point_mppt: int, session: AsyncSession) -> int:
        pass

    @abstractmethod
    async def add_panel_point(self, id_template: int, point_panel: PointMpptBase, id_point_string: int, session: AsyncSession):
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

    async def get_mppt_point_formatted(self, id_template: int, session: AsyncSession) -> list[PointMppt]:
        point_mppt = await self.get_mppt_point(id_template, session)
        response = []
        for point in point_mppt:
            adding_children = PointMppt(**point.__dict__, children=[])

            config_points = await self.get_mppt_config_point(id_template, point.id, session)
            for config_point in config_points:
                adding_children.children.append(PointMpptBase(**config_point.__dict__))

            string_points = await self.get_string_point(id_template, point.id, session)
            for string_point in string_points:
                adding_string_children = PointString(**string_point.__dict__, children=[])

                panel_points = await self.get_panel_point(id_template, string_point.id, session)
                for panel_point in panel_points:
                    adding_string_children.children.append(PointMpptBase(**panel_point.__dict__))
                adding_children.children.append(adding_string_children)
            response.append(adding_children)

        return response

    @async_db_request_handler
    async def add_formatted_mppt(self,
                                 formatted_points: list[PointMppt],
                                 new_template_id: int,
                                 session: AsyncSession):

        for point in formatted_points:
            new_mppt = await self.add_point_mppt(new_template_id, point, session)

            for point_string in point.children:
                new_string = await self.add_string_point(new_template_id, point_string, new_mppt, session)

                if point_string.id_config_information == PointType().MPPT_VOLTAGE or \
                        point_string.id_config_information == PointType().MPPT_CURRENT:
                    continue

                for panel_point in point_string.children:
                    await self.add_panel_point(new_template_id, panel_point, new_string, session)

        await session.commit()
        return "MPPT Points added successfully"


@Injectable
class NormalPointMpptService(PointMpptService):

    @async_db_request_handler
    async def add_point_mppt(self, id_template: int, point_mppt: PointMppt, session: AsyncSession):
        new_point_mppt = PointMpptEntity(
            **point_mppt.dict(exclude={"id", "children", "register_value"}),
            id_template=id_template,
            register=point_mppt.register_value
        )
        session.add(new_point_mppt)
        await session.flush()
        return new_point_mppt.id

    @async_db_request_handler
    async def add_string_point(self, id_template: int,
                               point_string: PointString,
                               id_point_mppt: int,
                               session: AsyncSession) -> int:
        new_point_string = PointMpptEntity(
            **point_string.dict(exclude={"id", "children", "register_value", "parent"}),
            id_template=id_template,
            parent=id_point_mppt,
            register=point_string.register_value
        )
        session.add(new_point_string)
        await session.flush()
        return new_point_string.id

    @async_db_request_handler
    async def add_panel_point(self, id_template: int,
                              point_panel: PointMpptBase,
                              id_point_string: int,
                              session: AsyncSession):
        new_point_panel = PointMpptEntity(
            **point_panel.dict(exclude={"id", "children", "register_value", "parent"}),
            id_template=id_template,
            parent=id_point_string,
            register=point_panel.register_value
        )
        session.add(new_point_panel)
        await session.flush()
        return new_point_panel.id

    @async_db_request_handler
    async def get_mppt_point(self, id_template: int, session: AsyncSession):
        query = (select(PointMpptEntity)
                 .where(PointMpptEntity.id_template == id_template)
                 .where(PointMpptEntity.id_config_information == PointType().MPPT_POINT)
                 .where(PointMpptEntity.status == 1))
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_mppt_config_point(self, id_template: int, id_point_mppt: int, session: AsyncSession):
        query = (select(PointMpptEntity)
                 .where(PointMpptEntity.id_template == id_template)
                 .where(PointMpptEntity.parent == id_point_mppt)
                 .filter((PointMpptEntity.id_config_information == PointType().MPPT_VOLTAGE) |
                         (PointMpptEntity.id_config_information == PointType().MPPT_CURRENT))
                 .where(PointMpptEntity.status == 1))
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_string_point(self, id_template: int, id_point_mppt: int, session: AsyncSession):
        query = (select(PointMpptEntity)
                 .where(PointMpptEntity.id_template == id_template)
                 .where(PointMpptEntity.parent == id_point_mppt)
                 .where(PointMpptEntity.id_config_information == PointType().MPPT_STRING)
                 .where(PointMpptEntity.status == 1))
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_panel_point(self, id_template: int, id_point_string: int, session: AsyncSession):
        query = (select(PointMpptEntity)
                 .where(PointMpptEntity.id_template == id_template)
                 .where(PointMpptEntity.parent == id_point_string)
                 .where(PointMpptEntity.id_config_information == PointType().MPPT_PANEL)
                 .where(PointMpptEntity.status == 1))
        result = await session.execute(query)
        return result.scalars().all()


@Injectable
class ManualPointMpptService(PointMpptService):
    @async_db_request_handler
    async def add_point_mppt(self, point_mppt: PointMppt, session: AsyncSession):
        pass

    @async_db_request_handler
    async def add_string_point(self, point_string: PointString, id_point_mppt: int, session: AsyncSession) -> int:
        pass

    @async_db_request_handler
    async def add_panel_point(self, point_panel: PointMpptBase, id_point_string: int, session: AsyncSession):
        pass

    @async_db_request_handler
    async def get_mppt_point(self, id_device_type: int, session: AsyncSession):
        query = (select(ManualPointMpptEntity)
                 .where(ManualPointMpptEntity.id_device_type == id_device_type)
                 .where(ManualPointMpptEntity.id_config_information == PointType().MPPT_POINT))
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_mppt_config_point(self, id_device_type: int, id_point_mppt: int, session: AsyncSession):
        query = (select(ManualPointMpptEntity)
                 .where(ManualPointMpptEntity.id_device_type == id_device_type)
                 .where(ManualPointMpptEntity.parent == id_point_mppt)
                 .filter((ManualPointMpptEntity.id_config_information == PointType().MPPT_VOLTAGE) |
                         (ManualPointMpptEntity.id_config_information == PointType().MPPT_CURRENT))
                 .where(ManualPointMpptEntity.status == 1))
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_string_point(self, id_device_type: int, id_point_mppt: int, session: AsyncSession):
        query = (select(ManualPointMpptEntity)
                 .where(ManualPointMpptEntity.id_device_type == id_device_type)
                 .where(ManualPointMpptEntity.parent == id_point_mppt)
                 .where(ManualPointMpptEntity.id_config_information == PointType().MPPT_STRING)
                 .where(ManualPointMpptEntity.status == 1))
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_panel_point(self, id_device_type: int, id_point_string: int, session: AsyncSession):
        query = (select(ManualPointMpptEntity)
                 .where(ManualPointMpptEntity.id_device_type == id_device_type)
                 .where(ManualPointMpptEntity.parent == id_point_string)
                 .where(ManualPointMpptEntity.id_config_information == PointType().MPPT_PANEL)
                 .where(ManualPointMpptEntity.status == 1))
        result = await session.execute(query)
        return result.scalars().all()
