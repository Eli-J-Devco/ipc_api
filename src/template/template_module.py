# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from nest.core import Module
from .template_controller import TemplateController
from .template_service import TemplateService
from ..devices.devices_service import DevicesService
from ..point.point_service import PointService
from ..point_control.point_control_service import PointControlService
from ..point_external.point_external_normal_service import NormalPointExternalService
from ..point_external.point_external_manual_service import ManualPointExternalService
from ..register_block.register_block_service import RegisterBlockService


@Module(
    controllers=[TemplateController],
    providers=[TemplateService,
               ManualPointExternalService,
               NormalPointExternalService,
               PointService,
               RegisterBlockService,
               PointControlService,
               DevicesService],
    imports=[],
    exports=[TemplateService]
)   
class TemplateModule:
    pass

    