from nest.core import Module
from .point_controller import PointController
from .point_service import PointService


@Module(
    controllers=[PointController],
    providers=[PointService],
    imports=[]
)   
class PointModule:
    pass

    