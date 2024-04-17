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

    