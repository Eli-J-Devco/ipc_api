# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from nest.core import Module
from .point_mppt_controller import PointMpptController
from .point_mppt_service import PointMpptService


@Module(
    controllers=[PointMpptController],
    providers=[PointMpptService],
    imports=[]
)   
class PointMpptModule:
    pass

    