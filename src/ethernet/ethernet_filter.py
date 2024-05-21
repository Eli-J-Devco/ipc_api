# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from pydantic import BaseModel

from .ethernet_model import Ethernet


class GetEthernetFilter(BaseModel):
    id: int


class UpdateEthernetFilter(Ethernet):
    pass
