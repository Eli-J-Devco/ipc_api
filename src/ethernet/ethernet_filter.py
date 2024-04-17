from pydantic import BaseModel

from .ethernet_model import Ethernet


class GetEthernetFilter(BaseModel):
    id: int


class UpdateEthernetFilter(Ethernet):
    pass
