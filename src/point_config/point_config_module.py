from nest.core import Module
from .point_config_controller import PointConfigController
from .point_config_service import PointConfigService
from ..project_setup.project_setup_service import ProjectSetupService


@Module(
    controllers=[PointConfigController],
    providers=[PointConfigService, ProjectSetupService],
    imports=[],
    exports=[PointConfigService]
)   
class PointConfigModule:
    pass

    