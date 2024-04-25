import json
import logging

from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .template_entity import Template as TemplateEntity
from .template_filter import GetTemplateFilter
from .template_model import Template, TemplateOutput
from ..devices.devices_service import DevicesService
from ..point.point_service import PointService
from ..point_mppt.point_mppt_service import ManualPointMpptService, NormalPointMpptService
from ..utils.service_wrapper import ServiceWrapper


@Injectable
class TemplateService:
    def __init__(self,
                 manual_point_mppt_service: ManualPointMpptService,
                 point_mppt_service: NormalPointMpptService,
                 point_service: PointService,
                 devices_service: DevicesService):
        self.manual_point_mppt_service = manual_point_mppt_service
        self.point_mppt_service = point_mppt_service
        self.point_service = point_service
        self.devices_service = devices_service

    @async_db_request_handler
    async def get_template(self, session: AsyncSession):
        query = select(TemplateEntity)
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
                raise HTTPException(status_code=result.status_code, detail=json
                                    .loads(result.body.decode("utf-8"))["message"])

        result = await ServiceWrapper.async_wrapper(self.point_mppt_service
                                                    .add_formatted_mppt)(points_to_add.point_mppt,
                                                                         new_template.id,
                                                                         session)

        if isinstance(result, JSONResponse):
            if result.status_code != status.HTTP_200_OK:
                raise HTTPException(status_code=result.status_code, detail=json
                                    .loads(result.body.decode("utf-8"))["message"])

        await session.commit()
        return "Template added successfully"
