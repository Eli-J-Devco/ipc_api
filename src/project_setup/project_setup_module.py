# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from nest.core import Module
from .project_setup_controller import ProjectSetupController
from .project_setup_service import ProjectSetupService


@Module(
    controllers=[ProjectSetupController],
    providers=[ProjectSetupService],
    imports=[]
)   
class ProjectSetupModule:
    pass

    