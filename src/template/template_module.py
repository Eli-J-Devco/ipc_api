from nest.core import Module
from .template_controller import TemplateController
from .template_service import TemplateService
from ..devices.devices_service import DevicesService
from ..point.point_service import PointService
from ..point_mppt.point_mppt_service import ManualPointMpptService, NormalPointMpptService


@Module(
    controllers=[TemplateController],
    providers=[TemplateService,
               ManualPointMpptService,
               NormalPointMpptService,
               PointService,
               DevicesService],
    imports=[],
    exports=[TemplateService]
)   
class TemplateModule:
    pass

    