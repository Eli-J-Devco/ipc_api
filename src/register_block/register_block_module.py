# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from nest.core import Module
from .register_block_controller import RegisterBlockController
from .register_block_service import RegisterBlockService
from ..project_setup.project_setup_service import ProjectSetupService
from ..template.template_service import TemplateService


@Module(
    controllers=[RegisterBlockController],
    providers=[RegisterBlockService, TemplateService, ProjectSetupService],
    imports=[],
    exports=[RegisterBlockService]
)   
class RegisterBlockModule:
    pass

    