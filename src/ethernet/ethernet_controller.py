# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/

from nest.core import Controller, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .ethernet_filter import GetEthernetFilter, UpdateEthernetFilter
from .ethernet_service import EthernetService
from ..authentication.authentication_model import Authentication
from ..authentication.authentication_repository import get_current_user
from ..config import config
from ..utils.service_wrapper import ServiceWrapper


@Controller("ethernet")
class EthernetController:

    def __init__(self, ethernet_service: EthernetService):
        self.ethernet_service = ethernet_service

    @Post("/get/")
    async def get_ethernet(self,
                           body: GetEthernetFilter,
                           session: AsyncSession = Depends(config.get_db),
                           user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper.async_wrapper(self.ethernet_service.get_ethernet_by_id)(body.id, session))

    @Post("/update/")
    async def update_ethernet(self,
                              ethernet: UpdateEthernetFilter,
                              session: AsyncSession = Depends(config.get_db),
                              user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper.async_wrapper(self.ethernet_service.update_ethernet)(ethernet, session))

    @Post("/ifconfig/")
    async def get_ifconfig(self,
                           session: AsyncSession = Depends(config.get_db),
                           user: Authentication = Depends(get_current_user)):
        network = ServiceWrapper.sync_wrapper(self.ethernet_service.get_network_config)()
        mode = await ServiceWrapper.async_wrapper(self.ethernet_service.get_ethernet_mode)(session)

        return {"network": network, "mode": mode}
