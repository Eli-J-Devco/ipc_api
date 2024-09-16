# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from nest.core import Module
from .point_external_controller import PointExternalController
from .point_external_service import PointExternalService


@Module(
    controllers=[PointExternalController],
    providers=[PointExternalService],
    imports=[]
)   
class PointMpptModule:
    pass

    