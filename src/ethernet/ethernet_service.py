# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import logging

import netifaces
from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable
from fastapi.responses import JSONResponse
from fastapi import status, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from .ethernet_entity import Ethernet as EthernetEntity
from .ethernet_filter import UpdateEthernetFilter
from .ethernet_helper import NetworkInterfaceConfig, UpdateNetworkInterfaceConfig
from .ethernet_model import EthernetConfig, Ethernet, EthernetDetails
from ..config import env_config
from ..project_setup.project_setup_filter import ConfigInformationType
from ..project_setup.project_setup_service import ProjectSetupService


@Injectable
class EthernetService:
    @async_db_request_handler
    async def get_ethernet_by_id(self, ethernet_id: int, session: AsyncSession) -> Ethernet:
        """
        Get ethernet by ID
        :author: nhan.tran
        :date: 20-05-2024
        :param ethernet_id:
        :param session:
        :return: Ethernet
        """
        if not ethernet_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ethernet ID is required")

        query = (select(EthernetEntity)
                 .options(selectinload(EthernetEntity.type_ethernet))
                 .where(EthernetEntity.id == ethernet_id))
        result = await session.execute(query)
        output = result.scalars().first()
        if not output:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ethernet not found")

        return Ethernet(**output.__dict__)

    @async_db_request_handler
    async def update_ethernet(self, update_ethernet: UpdateEthernetFilter, session: AsyncSession) -> EthernetDetails:
        """
        Update ethernet by ID
        :author: nhan.tran
        :date: 20-05-2024
        :param update_ethernet:
        :param session:
        :return: EthernetDetails
        """
        if not update_ethernet.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ethernet ID is required")

        query = select(EthernetEntity).where(EthernetEntity.id == update_ethernet.id)
        result = await session.execute(query)
        ethernet = result.scalars().first()

        if not ethernet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ethernet not found")

        ethernet = Ethernet(**ethernet.__dict__)
        ethernet = ethernet.copy(update=update_ethernet.dict(exclude_unset=True))

        query = (update(EthernetEntity)
                 .where(EthernetEntity.id == ethernet.id)
                 .values(**ethernet.dict()))

        await session.execute(query)

        query = (select(EthernetEntity)
                 .options(selectinload(EthernetEntity.type_ethernet))
                 .where(EthernetEntity.id == update_ethernet.id))
        result = await session.execute(query)
        updated_ethernet = result.scalars().first()
        update_ethernet_config = UpdateNetworkInterfaceConfig(EthernetDetails(**updated_ethernet.__dict__))
        update_ethernet_config.create_network_config(env_config.PATH_FILE_NETWORK_INTERFACE)

        await session.commit()
        return EthernetDetails(**updated_ethernet.__dict__)

    @async_db_request_handler
    async def get_ethernet_mode(self, session: AsyncSession) -> list[dict]:
        """
        Get ethernet mode
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :return: list[dict]
        """
        mode = await ProjectSetupService().get_config_information_by_type(session, ConfigInformationType.TYPE_ETHERNET)
        return mode

    @staticmethod
    def get_network_config() -> list[dict]:
        """
        Get network config
        :author: nhan.tran
        :date: 20-05-2024
        :return: list[dict]
        """
        interfaces = netifaces.interfaces()
        builtin_nics = []
        for interface in interfaces:
            builtin_nics.append(NetworkInterfaceConfig(nic=EthernetConfig(namekey=interface)).get_network_config())

        return builtin_nics
