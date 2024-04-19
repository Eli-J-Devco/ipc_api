from typing import Optional
from pydantic import BaseModel
from pydantic.fields import Field


class ScreenBase(BaseModel):
    id: Optional[int] = None
    screen_name: Optional[str] = None
    description: Optional[str] = None
    path: Optional[str] = None

    class Config:
        orm_mode = True


class ConfigInformationShort(BaseModel):
    id: int
    name: str


class ProjectSetup(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    serial_number: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    administrative_contact: Optional[str] = None

    id_first_page_on_login: Optional[int] = None
    id_logging_interval: Optional[int] = None
    id_scheduled_upload_time: Optional[int] = None
    number_times_retry: Optional[int] = None
    id_time_wait_before_retry: Optional[int] = None
    id_upload_debug_information: Optional[int] = None
    enable_upload_data_on_alarm_status: Optional[bool] = None
    enable_upload_data_on_low_disk: Optional[bool] = None
    enable_upload_data_on_system_startup: Optional[bool] = None

    link_remote_access: Optional[str] = None
    allow_remote_access: Optional[bool] = None

    id_time_zone: Optional[int] = None
    Time1cycle: Optional[float] = None
    sampling_time1cycle: Optional[float] = None

    enable_zero_export: Optional[bool] = None
    value_zero_export: Optional[float] = None

    enable_limit_energy: Optional[bool] = None
    value_limit_energy: Optional[float] = None

    modhopper1: Optional[int] = None
    modhopper2: Optional[int] = None
    modhopper_key: Optional[str] = None
    modhopper_rf_config: Optional[int] = None
    modhopper_rf_channel: Optional[int] = None
    status: Optional[bool] = None
    logging_interval: ConfigInformationShort
    logging_interval_list: list[ConfigInformationShort]
    first_page_on_login: ScreenBase
    screen_list: list[ScreenBase]

    class Config:
        orm_mode = True


class ConfigType(BaseModel):
    id: int
    name: str
    status: bool

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
        validate_assignment = True


class ConfigInformation(ConfigInformationShort):
    parent: Optional[int] = None
    namekey: Optional[str] = None
    description: Optional[str] = None
    value: Optional[str] = None
    id_type: Optional[int] = None
    type: Optional[int] = None
    status: Optional[bool] = None
    id_pointclass_type: Optional[int] = None

    class Config:
        orm_mode = True


class FirstPageOnLogin(BaseModel):
    screen_name: Optional[str] = None
    description: Optional[str] = None
    path: Optional[str] = None

    class Config:
        orm_mode = True


class RemoteAccessInformation(BaseModel):
    link_remote_access: Optional[str] = None
    allow_remote_access: Optional[bool] = None

    class Config:
        orm_mode = True
