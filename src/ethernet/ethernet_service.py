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


@Injectable
class EthernetService:
    @async_db_request_handler
    async def get_ethernet_by_id(self, ethernet_id: int, session: AsyncSession):
        query = (select(EthernetEntity)
                 .options(selectinload(EthernetEntity.type_ethernet))
                 .where(EthernetEntity.id == ethernet_id))
        result = await session.execute(query)
        output = result.scalars().first()
        if not output:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ethernet not found")

        return Ethernet(**output.__dict__)

    @async_db_request_handler
    async def update_ethernet(self, update_ethernet: UpdateEthernetFilter, session: AsyncSession):
        query = select(EthernetEntity).where(EthernetEntity.id == update_ethernet.id)
        result = await session.execute(query)
        ethernet = result.scalars().first()

        if not ethernet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ethernet not found")

        query = (update(EthernetEntity)
                 .where(EthernetEntity.id == ethernet.id)
                 .values(**update_ethernet.__dict__))

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

    @staticmethod
    def get_network_config():
        interfaces = netifaces.interfaces()
        builtin_nics = []
        for interface in interfaces:
            builtin_nics.append(NetworkInterfaceConfig(nic=EthernetConfig(namekey=interface)).get_network_config())

        return builtin_nics
