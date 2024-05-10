from typing import Optional

from pydantic import BaseModel

from ..project_setup.project_setup_model import ConfigInformationShort


class Rs485Short(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class Rs485(Rs485Short):
    namekey: Optional[str] = None
    id_driver_list: Optional[int] = None
    id_type_baud_rates: Optional[int] = None
    id_type_parity: Optional[int] = None
    id_type_stopbits: Optional[int] = None
    id_type_timeout: Optional[int] = None
    id_type_debug_level: Optional[int] = None


class Rs485Config(BaseModel):
    baud_rates: list[ConfigInformationShort]
    parities: list[ConfigInformationShort]
    stop_bits: list[ConfigInformationShort]
    timeouts: list[ConfigInformationShort]
    debug_levels: list[ConfigInformationShort]


class SerialPort(BaseModel):
    serial_port: str
