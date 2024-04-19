from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import serial.tools.list_ports as ports

from .rs485_entity import Rs485 as Rs485Entity
from .rs485_model import Rs485, Rs485Config, SerialPort
from ..project_setup.project_setup_entity import ConfigInformation as ConfigInformationEntity
from ..project_setup.project_setup_filter import ConfigInformationEnum


@Injectable
class Rs485Service:
    @async_db_request_handler
    async def get_rs485_by_id(self, rs485_id: int, session: AsyncSession):
        query = select(Rs485Entity).where(Rs485Entity.id == rs485_id)
        result = await session.execute(query)
        output = result.scalars().first()
        if not output:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RS485 not found")

        return Rs485(**output.__dict__)

    @async_db_request_handler
    async def update_rs485(self, rs485: Rs485, session: AsyncSession):
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
    async def rs485_config(self, session: AsyncSession):
        baud_rate_query = (select(ConfigInformationEntity)
                           .where(ConfigInformationEntity.id > ConfigInformationEnum.TYPE_BAUD_RATE.MIN)
                           .where(ConfigInformationEntity.id <= ConfigInformationEnum.TYPE_BAUD_RATE.MAX))

        parity_query = (select(ConfigInformationEntity)
                        .where(ConfigInformationEntity.id > ConfigInformationEnum.TYPE_PARITY.MIN)
                        .where(ConfigInformationEntity.id <= ConfigInformationEnum.TYPE_PARITY.MAX))

        stop_bits_query = (select(ConfigInformationEntity)
                           .where(ConfigInformationEntity.id > ConfigInformationEnum.TYPE_STOP_BIT.MIN)
                           .where(ConfigInformationEntity.id <= ConfigInformationEnum.TYPE_STOP_BIT.MAX))

        debug_level_query = (select(ConfigInformationEntity)
                             .where(ConfigInformationEntity.id > ConfigInformationEnum.TYPE_MODBUS_DEBUG_LEVEL.MIN)
                             .where(ConfigInformationEntity.id <= ConfigInformationEnum.TYPE_MODBUS_DEBUG_LEVEL.MAX))

        timeout_query = (select(ConfigInformationEntity)
                         .where(ConfigInformationEntity.id > ConfigInformationEnum.TYPE_MODBUS_TIMEOUT.MIN)
                         .where(ConfigInformationEntity.id <= ConfigInformationEnum.TYPE_MODBUS_TIMEOUT.MAX))

        baud_rate = await session.execute(baud_rate_query)
        parity = await session.execute(parity_query)
        stop_bits = await session.execute(stop_bits_query)
        debug_level = await session.execute(debug_level_query)
        timeout = await session.execute(timeout_query)

        baud_rates = baud_rate.scalars().all()
        parities = parity.scalars().all()
        stop_bits = stop_bits.scalars().all()
        debug_levels = debug_level.scalars().all()
        timeouts = timeout.scalars().all()

        return Rs485Config(
                baud_rates=[baud_rate.__dict__ for baud_rate in baud_rates],
                parities=[parity.__dict__ for parity in parities],
                stop_bits=[stop_bit.__dict__ for stop_bit in stop_bits],
                debug_levels=[debug_level.__dict__ for debug_level in debug_levels],
                timeouts=[timeout.__dict__ for timeout in timeouts]
        )

    @staticmethod
    def get_serial_ports():
        return [SerialPort(serial_port=port.device) for port in ports.comports()]
