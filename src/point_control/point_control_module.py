from nest.core import Module
from .point_control_controller import PointControlController
from .point_control_service import PointControlService
from ..point.point_service import PointService
from ..point_config.point_config_service import PointConfigService


@Module(
    controllers=[PointControlController],
    providers=[PointControlService, PointService, PointConfigService],
    imports=[],
    exports=[PointControlService]
)
class PointControlModule:
    pass

    