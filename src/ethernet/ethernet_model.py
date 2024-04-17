from typing import Optional

from pydantic import BaseModel

from ..project_setup.project_setup_model import ConfigInformation


class EthernetConfig(BaseModel):
    namekey: str
    allow_dns: Optional[bool] = None
    ip_address: Optional[str] = None
    subnet_mask: Optional[str] = None
    gateway: Optional[str] = None
    mtu: Optional[str] = None
    dns1: Optional[str] = None
    dns2: Optional[str] = None


class Ethernet(EthernetConfig):
    name: str
    id: int
    id_type_ethernet: int


class EthernetDetails(Ethernet):
    type_ethernet: Optional[ConfigInformation] = None

    class Config:
        orm_mode = True
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True
        validate_assignment = True
