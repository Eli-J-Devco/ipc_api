# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from nest.core import Controller, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .rs485_service import Rs485Service
from .rs485_model import Rs485
from .rs485_filter import RS485Filter

from ..config import config
from ..authentication.authentication_repository import get_current_user
from ..authentication.authentication_model import Authentication
from ..utils.service_wrapper import ServiceWrapper


@Controller("rs485")
class Rs485Controller:

    def __init__(self, rs485_service: Rs485Service):
        self.rs485_service = rs485_service

    @Post("/get/")
    async def get_rs485(self,
                        rs485: RS485Filter,
                        session: AsyncSession = Depends(config.get_db),
                        user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.rs485_service.get_rs485_by_id)(rs485.id, session)

    @Post("/update/")
    async def update_rs485(self,
                           rs485: Rs485,
                           session: AsyncSession = Depends(config.get_db),
                           user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.rs485_service.update_rs485)(rs485, session)

    @Post("/config/")
    async def rs485_config(self,
                           session: AsyncSession = Depends(config.get_db),
                           user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.rs485_service.rs485_config)(session)

    @Post("/serial_ports/")
    async def get_serial_ports(self,
                               user: Authentication = Depends(get_current_user)):
        return ServiceWrapper.sync_wrapper(self.rs485_service.get_serial_ports)()
