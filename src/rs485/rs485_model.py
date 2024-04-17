from pydantic import BaseModel

from ..project_setup.project_setup_model import ConfigInformationShort


class Rs485(BaseModel):
    id: int
    name: str
    namekey: str
    id_driver_list: int
    id_type_baud_rates: int
    id_type_parity: int
    id_type_stopbits: int
    id_type_timeout: int
    id_type_debug_level: int


class Rs485Config(BaseModel):
    baud_rates: list[ConfigInformationShort]
    parities: list[ConfigInformationShort]
    stop_bits: list[ConfigInformationShort]
    timeouts: list[ConfigInformationShort]
    debug_levels: list[ConfigInformationShort]


class SerialPort(BaseModel):
    serial_port: str
