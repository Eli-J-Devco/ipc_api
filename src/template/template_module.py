from nest.core import Module
from .template_controller import TemplateController
from .template_service import TemplateService


@Module(
    controllers=[TemplateController],
    providers=[TemplateService],
    imports=[]
)   
class TemplateModule:
    pass

    