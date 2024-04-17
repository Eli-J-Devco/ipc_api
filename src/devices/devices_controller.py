import logging

from nest.core import Controller, Get, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .devices_service import DevicesService
from .devices_model import Devices
from ..authentication.authentication_model import Authentication
from ..authentication.authentication_repository import get_current_user
from ..config import config


@Controller("devices")
class DevicesController:
    def __init__(self, devices_service: DevicesService):
        self.devices_service = devices_service

    @Post("/get/")
    async def get_devices(self, session: AsyncSession = Depends(config.get_db),
                          auth: Authentication = Depends(get_current_user)):
        return await self.devices_service.get_devices(session)

    @Post("/add/")
    async def add_devices(self,
                          devices: Devices, session: AsyncSession = Depends(config.get_db),
                          auth: Authentication = Depends(get_current_user)):
        return await self.devices_service.add_devices(devices, session)
