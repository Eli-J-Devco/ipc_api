# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import json
from typing import Sequence

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from .template_entity import Template as TemplateEntity
from .template_filter import GetTemplateFilter
from .template_model import GetTemplate, TemplateOutput, TemplateConfig, TemplateBase
from ..devices.devices_service import DevicesService
from ..point.point_entity import Point as PointEntity
from ..point.point_model import PointBase
from ..point.point_filter import AddPointListFilter
from ..point.point_service import PointService
from ..point_config.point_config_model import PointListControlGroupChildren
from ..point_config.point_config_service import PointConfigService
from ..point_config.point_control_group_config_service import PointControlGroupConfigService
from ..point_control.point_control_entity import PointControl as PointControlEntity
from ..point_control.point_control_service import PointControlService
from ..point_mppt.point_mppt_manual_service import ManualPointMpptService
from ..point_mppt.point_mppt_normal_service import NormalPointMpptService
from ..project_setup.project_setup_service import ProjectSetupService
from ..register_block.register_block_service import RegisterBlockService
from ..utils.service_wrapper import ServiceWrapper


@Injectable
class TemplateService:
    def __init__(self,
                 manual_point_mppt_service: ManualPointMpptService,
                 point_mppt_service: NormalPointMpptService,
                 point_service: PointService,
                 register_block_service: RegisterBlockService,
                 point_control_service: PointControlService,
                 devices_service: DevicesService):
        self.manual_point_mppt_service = manual_point_mppt_service
        self.point_mppt_service = point_mppt_service
        self.point_service = point_service
        self.register_block_service = register_block_service
        self.point_control_service = point_control_service
        self.devices_service = devices_service

    @async_db_request_handler
    async def get_template(self, body: GetTemplateFilter,
                           session: AsyncSession) -> Sequence[TemplateBase] | TemplateOutput:
        """
        Get template
        :author: nhan.tran
        :date: 20-05-2024
        :param body:
        :param session:
        :return: Sequence[TemplateEntity] | TemplateOutput
        """
        if body.id is not None:
            query = select(TemplateEntity).where(TemplateEntity.id == body.id)
            result = await session.execute(query)
            template = result.scalars().first()
            if template.type != 1:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Method not allowed")
            return await ServiceWrapper.async_wrapper(self.get_template_detail)(template.name, body.id, session)

        if body.type is None:
            query = select(TemplateEntity)
        else:
            query = select(TemplateEntity).where(TemplateEntity.type == body.type)

        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_template_by_id(self, id_template: int,
                                 session: AsyncSession,
                                 func=None, *args, **kwargs) -> TemplateBase | TemplateOutput:
        """
        Get template by ID
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param session:
        :param func:
        :param args:
        :param kwargs:
        :return: TemplateBase | TemplateOutput
        """
        query = (select(TemplateEntity)
                 .where(TemplateEntity.id == id_template))
        result = await session.execute(query)
        template = result.scalars().first()
        if template is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TemplateBase not found")

        if func:
            return await ServiceWrapper.async_wrapper(func)(id_template, session, *args, **kwargs)

        return TemplateBase(**template.__dict__)

    @async_db_request_handler
    async def get_template_by_name(self, name: str,
                                   id_device_group: int,
                                   session: AsyncSession,
                                   func=None, *args, **kwargs) -> TemplateBase | TemplateOutput:
        """
        Get template by name
        :author: nhan.tran
        :date: 20-05-2024
        :param name:
        :param session:
        :param func:
        :param args:
        :param kwargs:
        :return:
        """
        query = (select(TemplateEntity)
                 .where(TemplateEntity.id_device_group == id_device_group)
                 .where(TemplateEntity.name == name))
        result = await session.execute(query)
        template = result.scalars().first()
        if template is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TemplateBase not found")

        if func:
            return await ServiceWrapper.async_wrapper(func)(name, session, *args, **kwargs)

        return TemplateBase(**template.__dict__)

    @async_db_request_handler
    async def get_manual(self, id_device_type: int, session: AsyncSession) -> TemplateOutput:
        """
        Get manual template by device type
        :author: nhan.tran
        :date: 20-05-2024
        :param id_device_type:
        :param session:
        :return: TemplateOutput
        """
        points = await self.point_service.get_manual_point_list(id_device_type, session)
        point_mppt = await self.manual_point_mppt_service.get_mppt_point_formatted(id_device_type, session)
        return TemplateOutput(points=points, point_mppt=point_mppt)

    @async_db_request_handler
    async def add_new_template(self, new_template: TemplateBase,
                               id_device_type: int,
                               session: AsyncSession) -> None | HTTPException:
        """
        Add new template
        :author: nhan.tran
        :date: 26-07-2024
        :param new_template:
        :param id_device_type:
        :param session:
        :return:
        """
        points_to_add = await self.get_manual(id_device_type, session)
        result = await self.point_service.add_point(session,
                                                    AddPointListFilter(
                                                        id_template=new_template.id,
                                                        point=points_to_add.points
                                                    ))

        if not result:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="Error adding point")

        result = await self.point_mppt_service.add_mppt_point_formatted(points_to_add.point_mppt,
                                                                        new_template.id,
                                                                        session)

        if not result:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="Error adding point mppt")

    @async_db_request_handler
    async def duplicate_template(self, id_template: int, new_template_id: int,
                                 session: AsyncSession) -> HTTPException | bool:
        """
        Duplicate template
        :author: nhan.tran
        :date: 26-07-2024
        :param id_template:
        :param new_template_id:
        :param session:
        :return: HTTPException | bool
        """
        points = await self.point_service.get_points(id_template, session)
        points_mppt = await self.point_mppt_service.get_mppt_point_formatted(id_template, session)
        points_control = await self.point_control_service.get_control_group_point(session, id_template)

        try:
            points = [PointEntity(**PointBase(**point)
                                  .dict(exclude={"register_value", "id"}),
                                  id_template=new_template_id,
                                  register=point["register"])
                      for point in points]
            session.add_all(points)
            await session.flush()
        except Exception as e:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail=f"Error adding point {e}")

        result = await self.point_mppt_service.add_mppt_point_formatted(points_mppt, new_template_id, session)
        if not result:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="Error adding point mppt")

        result = await self.point_control_service.add_control_group_with_points(points_control,
                                                                                new_template_id, session)
        if not result:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="Error adding point control")

        return True

    @async_db_request_handler
    async def get_template_detail(self, template: str, id_template: int, session: AsyncSession) -> TemplateOutput:
        """
        Get template detail by ID
        :author: nhan.tran
        :date: 20-05-2024
        :param template:
        :param id_template:
        :param session:
        :return: TemplateOutput
        """
        points = await self.point_service.get_points(id_template, session)
        point_mppt = await self.point_mppt_service.get_mppt_point_formatted(id_template, session)
        point_string = await self.point_mppt_service.get_string_point_formatted(id_template, session)
        register_blocks = await self.register_block_service.get_register_block(id_template, session)
        point_controls = await self.point_control_service.get_control_group_point(session, id_template)
        device_group = await self.get_device_group_by_template(id_template, session)
        device_type = None
        if device_group is not None:
            id_device_type = await self.devices_service.utils_service.get_device_type_by_device_group(device_group,
                                                                                                      session)
            device_type = await self.devices_service.utils_service.get_device_type_by_id(id_device_type, session)

        return TemplateOutput(name=template,
                              points=points,
                              point_mppt=point_mppt,
                              point_string=point_string,
                              register_blocks=register_blocks,
                              point_controls=point_controls,
                              device_type=device_type.name)

    @async_db_request_handler
    async def get_device_group_by_template(self, id_template: int, session: AsyncSession) -> int:
        """
        Get device group by template
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param session:
        :return: int
        """
        query = (select(TemplateEntity.id_device_group)
                 .where(TemplateEntity.id == id_template))
        result = await session.execute(query)
        return int(result.scalars().first())

    @async_db_request_handler
    async def get_template_config(self, session: AsyncSession) -> TemplateConfig:
        """
        Get template config
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :return: TemplateConfig
        """
        project_setup_service = ProjectSetupService()
        point_config = await (ServiceWrapper
                              .async_wrapper(PointConfigService(project_setup_service)
                                             .get_all_config)(session))

        type_function = await (ServiceWrapper
                               .async_wrapper(RegisterBlockService(project_setup_service)
                                              .get_type_function)(session))

        return TemplateConfig(
            **json.loads(point_config.body.decode("utf8")) if isinstance(point_config, JSONResponse) else point_config,
            type_function=json.loads(type_function.body.decode("utf8"))
            if isinstance(type_function, JSONResponse) else type_function)

    @async_db_request_handler
    async def add_template(self, session: AsyncSession, new_template: TemplateBase) -> dict[str, int] | HTTPException:
        """
        Add template
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :param new_template:
        :return: dict[str, int] | HTTPException
        """
        if new_template.name is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name is required")

        if new_template.id_device_group is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Device group is required")

        id_device_type = await (self.devices_service
                                .utils_service.get_device_type_by_device_group(new_template.id_device_group,
                                                                               session))
        if id_device_type is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device type not found")

        add_template = TemplateEntity(
            **new_template.dict(exclude_unset=True, exclude={"id"})
        )

        session.add(add_template)
        await session.flush()

        result = None
        if new_template.id is None:
            result = await self.add_new_template(add_template, id_device_type, session)
        else:
            result = await self.duplicate_template(new_template.id, add_template.id, session)

        if isinstance(result, HTTPException):
            return result

        await session.commit()
        return {
            "id": add_template.id,
            "data": await self.get_template(GetTemplateFilter(type=1), session)
        }

    @async_db_request_handler
    async def delete_template(self, id_template: int,
                              session: AsyncSession) -> Sequence[TemplateBase] | TemplateOutput | HTTPException:
        """
        Delete template
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param session:
        :return: Sequence[TemplateBase] | TemplateOutput | HTTPException
        """
        devices = await self.devices_service.get_device_by_template(id_template, session)
        if devices:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="TemplateBase is in use and cannot be deleted")

        query = (delete(TemplateEntity)
                 .where(TemplateEntity.id == id_template))
        await session.execute(query)
        await session.commit()
        return await self.get_template(GetTemplateFilter(), session)

    @async_db_request_handler
    async def get_control_group_by_device_type(self, session: AsyncSession,
                                               id_template: int):
        id_device_group = await self.get_device_group_by_template(id_template, session)
        id_device_type = await self.devices_service.utils_service.get_device_type_by_device_group(id_device_group,
                                                                                                  session)
        if id_device_type is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device type not found")

        control_groups = await (PointControlGroupConfigService
                                .get_control_group_by_device_type(id_device_type, session))
        response = []
        for control_group in control_groups:
            query = (select(PointControlEntity)
                     .where(PointControlEntity.id_control_group == control_group.id)
                     .where(PointControlEntity.status == 1))
            result = await session.execute(query)
            points = jsonable_encoder(result.scalars().all())
            response.append(PointListControlGroupChildren(**control_group.__dict__, children=points))
        return response
