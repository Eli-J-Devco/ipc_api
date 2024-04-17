from nest.core import Module
from .rs485_controller import Rs485Controller
from .rs485_service import Rs485Service


@Module(
    controllers=[Rs485Controller],
    providers=[Rs485Service],
    imports=[]
)   
class Rs485Module:
    pass

    