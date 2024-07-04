# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import List, Any

from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import serial.tools.list_ports as ports

from .rs485_entity import Rs485 as Rs485Entity
from .rs485_model import Rs485, Rs485Config, SerialPort, Rs485Short
from ..project_setup.project_setup_entity import ConfigInformation as ConfigInformationEntity
from ..project_setup.project_setup_filter import ConfigInformationEnum


@Injectable
class Rs485Service:
    @async_db_request_handler
    async def get_rs485_by_id(self, rs485_id: int, session: AsyncSession) -> list[Rs485Short] | Rs485:
        """
        Get RS485 by ID
        :author: nhan.tran
        :date: 20-05-2024
        :param rs485_id:
        :param session:
        :return: list[Rs485Short] | Rs485
        """
        if not rs485_id:
            query = select(Rs485Entity).where(Rs485Entity.status == 1)
            result = await session.execute(query)
            return [Rs485Short(**jsonable_encoder(output)) for output in result.scalars().all()]

        query = select(Rs485Entity).where(Rs485Entity.id == rs485_id)
        result = await session.execute(query)
        output = result.scalars().first()
        if not output:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RS485 not found")

        return Rs485(**output.__dict__)

    @async_db_request_handler
    async def update_rs485(self, rs485: Rs485, session: AsyncSession) -> Rs485:
        """
        Update RS485
        :author: nhan.tran
        :date: 20-05-2024
        :param rs485:
        :param session:
        :return: Rs485
        """
        if not rs485.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="RS485 ID is required")

        verify_rs485 = await self.get_rs485_by_id(rs485.id, session)
        if not verify_rs485:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RS485 not found")

        verify_rs485 = rs485.copy(update=rs485.dict(exclude_unset=True))
        query = (update(Rs485Entity).where(Rs485Entity.id == rs485.id).values(**verify_rs485.dict()))

        await session.execute(query)
        await session.commit()
        return verify_rs485

    @async_db_request_handler
    async def get_config(self, config_min: int,
                         config_max: int,
                         session: AsyncSession) -> list[Any]:
        """
        Get each config by range
        :author: nhan.tran
        :date: 20-05-2024
        :param config_min:
        :param config_max:
        :param session:
        :return: list[Any]
        """
        query = (select(ConfigInformationEntity)
                 .where(ConfigInformationEntity.id > config_min)
                 .where(ConfigInformationEntity.id <= config_max))
        result = await session.execute(query)
        config = result.scalars().all()
        return [jsonable_encoder(c) for c in config]

    @async_db_request_handler
    async def rs485_config(self, session: AsyncSession) -> Rs485Config:
        """
        Get RS485 config
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :return: Rs485Config
        """
        baud_rates = await self.get_config(ConfigInformationEnum.TYPE_BAUD_RATE.MIN,
                                           ConfigInformationEnum.TYPE_BAUD_RATE.MAX,
                                           session)

        parities = await self.get_config(ConfigInformationEnum.TYPE_PARITY.MIN,
                                         ConfigInformationEnum.TYPE_PARITY.MAX,
                                         session)

        stop_bits = await self.get_config(ConfigInformationEnum.TYPE_STOP_BIT.MIN,
                                          ConfigInformationEnum.TYPE_STOP_BIT.MAX,
                                          session)

        debug_levels = await self.get_config(ConfigInformationEnum.TYPE_MODBUS_DEBUG_LEVEL.MIN,
                                             ConfigInformationEnum.TYPE_MODBUS_DEBUG_LEVEL.MAX,
                                             session)

        timeouts = await self.get_config(ConfigInformationEnum.TYPE_MODBUS_TIMEOUT.MIN,
                                         ConfigInformationEnum.TYPE_MODBUS_TIMEOUT.MAX,
                                         session)

        return Rs485Config(
            baud_rates=baud_rates,
            parities=parities,
            stop_bits=stop_bits,
            debug_levels=debug_levels,
            timeouts=timeouts
        )

    @staticmethod
    def get_serial_ports() -> List[SerialPort]:
        """
        Get serial ports
        :author: nhan.tran
        :date: 20-05-2024
        :return: List[SerialPort]
        """
        return [SerialPort(serial_port=port.device) for port in ports.comports()]
