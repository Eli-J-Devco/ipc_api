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
from ..point_mppt.point_mppt_normal_service import NormalPointMpptService
from ..point_mppt.point_mppt_manual_service import ManualPointMpptService
from ..register_block.register_block_service import RegisterBlockService


@Module(
    controllers=[TemplateController],
    providers=[TemplateService,
               ManualPointMpptService,
               NormalPointMpptService,
               PointService,
               RegisterBlockService,
               PointControlService,
               DevicesService],
    imports=[],
    exports=[TemplateService]
)   
class TemplateModule:
    pass

    