# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/

import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from dbEntity.upload_channel.upload_channel_entity import UploadChannel
from dbEntity.project_setup.project_setup_entity import *
from dbModel.upload_channel_model import *
import logging
logger = logging.getLogger(__name__)
class UploadChannelService:
    @staticmethod
    async def select_type_log_file(session: AsyncSession, channel_id: int):
        try:
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
        except Exception as e:
            logger.error(f"Error: {e}")
            return None
        finally:
            await session.close()
            
    @staticmethod
    async def get_upload_url_by_id(session: AsyncSession, id_upload_channel: int):
        try:
            query = (
                select(UploadChannel)
                .where(UploadChannel.id == id_upload_channel)
            )
            result = await session.execute(query)
            upload_channel = result.scalar_one_or_none()

            if upload_channel:
                return UploadChannelModel.from_orm(upload_channel)

            return None
        except Exception as e:
            logger.error("Error in get_upload_url_by_id: ", e)
            return None
        finally:
            await session.close()