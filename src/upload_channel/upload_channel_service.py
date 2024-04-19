from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable
from fastapi import HTTPException, status

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .upload_channel_model import UploadChannel, UploadChannelConfig, UploadChannelConfigs
from .upload_channel_entity import UploadChannel as UploadChannelEntity, \
    UploadChannelDeviceMap as UploadChannelDeviceMapEntity

from ..devices.devices_model import DeviceUploadChannelMap
from ..devices.devices_service import DevicesService
from ..project_setup.project_setup_filter import ConfigInformationType
from ..project_setup.project_setup_service import ProjectSetupService


@Injectable
class UploadChannelService:

    @async_db_request_handler
    async def get_upload_channel(self, session: AsyncSession):
        query = (select(UploadChannelEntity)
                 .options(selectinload(UploadChannelEntity.type_protocol))
                 .options(selectinload(UploadChannelEntity.logging_interval)))
        result = await session.execute(query)
        channels = result.scalars().all()

        if not channels:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload Channel not found")

        output = []
        for channel in channels:
            channel_map_query = (select(UploadChannelDeviceMapEntity)
                                 .where(UploadChannelDeviceMapEntity.id_upload_channel == channel.id))
            result = await session.execute(channel_map_query)
            channel_map = result.scalars().all()

            devices = []
            for device in channel_map:
                device = await DevicesService().get_device_by_id(device.id_device, session)
                devices.append(DeviceUploadChannelMap(**device.dict()))

            type_protocol = channel.type_protocol.__dict__ if channel.type_protocol else None
            logging_interval = channel.logging_interval.__dict__ if channel.logging_interval else None
            devices = [device.__dict__ for device in devices]

            channel = UploadChannel(**channel.__dict__).dict(exclude_unset=True)
            output.append(UploadChannelConfig(**channel,
                                              type_protocol=type_protocol,
                                              logging_interval=logging_interval,
                                              devices=devices))

        return output

    @async_db_request_handler
    async def get_configs(self, session: AsyncSession):
        logging_intervals = await (ProjectSetupService()
                                   .get_config_information_by_type(session,
                                                                   ConfigInformationType.TYPE_LOGGING_INTERVAL))
        type_protocols = await (ProjectSetupService()
                                .get_config_information_by_type(session,
                                                                ConfigInformationType.TYPE_UPLOAD_PROTOCOL))
        devices = await DevicesService().get_devices(session)

        configs = UploadChannelConfigs(type_protocols=[type_protocol.__dict__
                                                       for type_protocol in type_protocols],
                                       logging_intervals=[logging_interval.__dict__
                                                          for logging_interval in logging_intervals],
                                       devices=devices).dict(exclude_unset=True)

        return configs

    @async_db_request_handler
    async def update_upload_channel(self, channels: list[UploadChannelConfig], session: AsyncSession):
        for channel in channels:
            # validate if channel configuration exists
            ProjectSetupService().validate_config_information(channel.id_type_protocol,
                                                              ConfigInformationType.TYPE_UPLOAD_PROTOCOL, )
            ProjectSetupService().validate_config_information(channel.id_type_logging_interval,
                                                              ConfigInformationType.TYPE_LOGGING_INTERVAL)

            query = (select(UploadChannelEntity)
                     .where(UploadChannelEntity.id == channel.id))
            result = await session.execute(query)
            updating_channel = result.scalars().first()

            if updating_channel:
                updating_channel = (UploadChannelConfig(**updating_channel.__dict__)
                                    .copy(update=channel
                                          .dict(exclude_unset=True)))
                query = (update(UploadChannelEntity)
                         .where(UploadChannelEntity.id == channel.id)
                         .values(updating_channel.dict(exclude_unset=True, exclude={"devices"})))

                await session.execute(query)
                await self.update_device_upload_map(session, channel.devices, channel.id)

        await session.commit()
        return "Updated upload channel successfully"

    @async_db_request_handler
    async def update_device_upload_map(self,
                                       session: AsyncSession,
                                       devices: list[DeviceUploadChannelMap],
                                       channel_id: int):
        if not devices:
            query = (delete(UploadChannelDeviceMapEntity)
                     .where(UploadChannelDeviceMapEntity.id_upload_channel == channel_id))
            await session.execute(query)
            await session.commit()
            return

        for device in devices:
            query = (select(UploadChannelDeviceMapEntity)
                     .where(UploadChannelDeviceMapEntity.id_device == device.id)
                     .where(UploadChannelDeviceMapEntity.id_upload_channel == channel_id))
            result = await session.execute(query)
            updating_device = result.scalars().first()

            if updating_device:
                continue

            new_device = UploadChannelDeviceMapEntity(id_device=device.id, id_upload_channel=channel_id)
            session.add(new_device)

        await session.commit()
        return
