# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from nest.core import Module
from .ethernet_controller import EthernetController
from .ethernet_service import EthernetService


@Module(
    controllers=[EthernetController],
    providers=[EthernetService],
    imports=[]
)   
class EthernetModule:
    pass

    