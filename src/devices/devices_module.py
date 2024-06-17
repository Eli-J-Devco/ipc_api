# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from nest.core import Module
from .devices_controller import DevicesController
from .devices_service import DevicesService
from .components_service import ComponentsService
from .devices_utils_service import UtilsService
from ..authentication.authentication_repository import AuthenticationRepository


@Module(
    controllers=[DevicesController],
    providers=[DevicesService, AuthenticationRepository, ComponentsService, UtilsService],
    imports=[],
    exports=[DevicesService]
)   
class DevicesModule:
    pass

    