# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from nest.core import Module
from .device_point_controller import DevicePointController
from .device_point_service import DevicePointService


@Module(
    controllers=[DevicePointController],
    providers=[DevicePointService],
    imports=[]
)   
class DevicePointModule:
    pass

    