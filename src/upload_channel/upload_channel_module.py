# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from nest.core import Module
from .upload_channel_controller import UploadChannelController
from .upload_channel_service import UploadChannelService


@Module(
    controllers=[UploadChannelController],
    providers=[UploadChannelService],
    imports=[]
)   
class UploadChannelModule:
    pass

    