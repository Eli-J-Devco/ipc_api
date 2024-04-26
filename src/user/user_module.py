from nest.core import Module
from .user_controller import UserController
from .user_service import UserService
from ..role.role_service import RoleService


@Module(
    controllers=[UserController],
    providers=[UserService, RoleService],
    imports=[],
    exports=[UserService]
)   
class UserModule:
    pass

    