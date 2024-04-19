from nest.core import Module
from .role_controller import RoleController
from .role_service import RoleService


@Module(
    controllers=[RoleController],
    providers=[RoleService],
    imports=[]
)   
class RoleModule:
    pass

    