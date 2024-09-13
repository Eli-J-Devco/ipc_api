# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/

import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from entity.upload_channel.upload_channel_entity import UploadChannel
from entity.project_setup.project_setup_entity import *
class UploadChannelService:
    @staticmethod
    async def select_type_log_file(session: AsyncSession,channel_id: int):
        # Tạo truy vấn để lấy thông tin từ upload_channel và config_information
        stmt = (
            select(
                UploadChannel.id.label('id_channel'),
                ConfigInformation.description.label('type_protocol')
            )
            .join(ConfigInformation, UploadChannel.id_type_protocol == ConfigInformation.id)
            .where(
                UploadChannel.id == channel_id,
                UploadChannel.status == 1
            )
        )

        result = await session.execute(stmt)
        channel_info = result.fetchone()

        if channel_info:
            return channel_info.type_protocol
        return None
    @staticmethod
    async def get_upload_url_by_id(session: AsyncSession, id_upload_channel: int):
        try:
            query = (
                select(UploadChannel.uploadurl)
                .where(UploadChannel.id == id_upload_channel)
            )
            result = await session.execute(query)
            upload_url = result.scalar()  # Lấy giá trị đầu tiên
            return upload_url
        except Exception as e:
            print("Error in get_upload_url_by_id: ", e)
            return None
        finally:
            await session.close()