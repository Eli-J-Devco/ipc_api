import json
import logging

from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .template_entity import Template as TemplateEntity
from .template_filter import GetTemplateFilter
from .template_model import Template, TemplateOutput, TemplateConfig

from ..devices.devices_service import DevicesService
from ..point.point_service import PointService
from ..point_config.point_config_service import PointConfigService
from ..point_control.point_control_service import PointControlService
from ..point_mppt.point_mppt_normal_service import NormalPointMpptService
from ..point_mppt.point_mppt_manual_service import ManualPointMpptService
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
    async def get_template(self, body: GetTemplateFilter, session: AsyncSession):
        if body.id is not None:
            query = select(TemplateEntity).where(TemplateEntity.id == body.id)
            result = await session.execute(query)
            if result.scalars().first().type != 1:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Method not allowed")
            return await ServiceWrapper.async_wrapper(self.get_template_detail)(body.id, session)

        if body.type is None:
            query = select(TemplateEntity)
        else:
            query = select(TemplateEntity).where(TemplateEntity.type == body.type)

        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_template_by_id(self, id_template: int, session: AsyncSession, func=None, *args, **kwargs):
        query = (select(TemplateEntity)
                 .where(TemplateEntity.id == id_template))
        result = await session.execute(query)
        template = result.scalars().first()
        if template is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

        if func:
            return await ServiceWrapper.async_wrapper(func)(id_template, session, *args, **kwargs)

        return template.__dict__

    @async_db_request_handler
    async def get_template_by_name(self, name: str, session: AsyncSession, func=None, *args, **kwargs):
        query = (select(TemplateEntity)
                 .where(TemplateEntity.name == name))
        result = await session.execute(query)
        template = result.scalars().first()
        if template is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

        if func:
            return await ServiceWrapper.async_wrapper(func)(name, session, *args, **kwargs)

        return template.__dict__

    @async_db_request_handler
    async def get_template_by_type(self, template_type: GetTemplateFilter, session: AsyncSession):
        query = (select(TemplateEntity)
                 .where(TemplateEntity.type == template_type.type))
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_manual(self, id_device_type: int, session: AsyncSession) -> TemplateOutput:
        points = await self.point_service.get_manual_point_list(id_device_type, session)
        point_mppt = await self.manual_point_mppt_service.get_mppt_point_formatted(id_device_type, session)
        return TemplateOutput(points=points, point_mppt=point_mppt)

    @async_db_request_handler
    async def get_template_detail(self, id_template: int, session: AsyncSession):
        points = await self.point_service.get_points(id_template, session)
        point_mppt = await self.point_mppt_service.get_mppt_point_formatted(id_template, session)
        register_blocks = await self.register_block_service.get_register_block(id_template, session)
        point_controls = await self.point_control_service.get_control_group_point(id_template, session)

        return TemplateOutput(points=points,
                              point_mppt=point_mppt,
                              register_blocks=register_blocks,
                              point_controls=point_controls)

    @async_db_request_handler
    async def get_template_config(self, session: AsyncSession):
        project_setup_service = ProjectSetupService()
        point_config = await (ServiceWrapper
                              .async_wrapper(PointConfigService(project_setup_service)
                                             .get_all_config)(session))

        type_function = await (ServiceWrapper
                               .async_wrapper(RegisterBlockService(project_setup_service)
                                              .get_type_function)(session))

        return TemplateConfig(**json.loads(point_config.body.decode("utf8"))
                              if isinstance(point_config, JSONResponse) else point_config,
                              type_function=json.loads(type_function.body.decode("utf8"))
                              if isinstance(type_function, JSONResponse) else type_function)

    @async_db_request_handler
    async def add_template(self, session: AsyncSession, new_template: Template):
        if new_template.name is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name is required")

        if new_template.id_device_group is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Device group is required")

        id_device_type = await self.devices_service.get_device_type_by_device_group(new_template.id_device_group,
                                                                                    session)
        if id_device_type is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device type not found")

        points_to_add = await self.get_manual(id_device_type, session)

        new_template = TemplateEntity(
            **new_template.dict(exclude_unset=True)
        )

        session.add(new_template)
        await session.flush()

        result = await ServiceWrapper.async_wrapper(self.point_service.add_point)(None,
                                                                                  session,
                                                                                  new_template.id,
                                                                                  points_to_add.points)

        if isinstance(result, JSONResponse):
            if result.status_code != status.HTTP_200_OK:
                return result

        result = await ServiceWrapper.async_wrapper(self.point_mppt_service
                                                    .add_formatted_mppt)(points_to_add.point_mppt,
                                                                         new_template.id,
                                                                         session)

        if isinstance(result, JSONResponse):
            if result.status_code != status.HTTP_200_OK:
                return result

        await session.commit()
        return "Template added successfully"

    @async_db_request_handler
    async def delete_template(self, id_template: int, session: AsyncSession):
        delete(TemplateEntity).where(TemplateEntity.id == id_template)
        await session.commit()
        return "Template deleted successfully"
