from nest.core import Controller, Get, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import config


from .template_service import TemplateService
from .template_model import Template
from ..authentication.authentication_repository import get_current_user
from ..authentication.authentication_model import Authentication


@Controller("template")
class TemplateController:

    def __init__(self, template_service: TemplateService):
        self.template_service = template_service

    @Post("/get/")
    async def get_template(self,
                           session: AsyncSession = Depends(config.get_db),
                           user: Authentication = Depends(get_current_user)):
        return await self.template_service.get_template(session)

    @Post("/add/")
    async def add_template(self, template: Template,
                           session: AsyncSession = Depends(config.get_db),
                           user: Authentication = Depends(get_current_user)):
        return await self.template_service.add_template(template, session)
 