from nest.core import Module
from .point_config_controller import PointConfigController
from .point_config_service import PointConfigService


@Module(
    controllers=[PointConfigController],
    providers=[PointConfigService],
    imports=[]
)   
class PointConfigModule:
    pass

    