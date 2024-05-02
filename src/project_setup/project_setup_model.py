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

    enable_power_limit: Optional[bool] = None
    value_power_limit: Optional[float] = None
    value_offset_power_limit: Optional[float] = None

    powermeter_target_point: Optional[float] = None
    powermeter_tolerance: Optional[float] = None
    powermeter_max_point: Optional[float] = None

    slow_approx_limit_in_percent: Optional[int] = None
    slow_approx_factor_in_percent: Optional[int] = None

    loop_interval_in_seconds: Optional[int] = None
    set_limit_delay_in_seconds: Optional[int] = None
    set_limit_timeout_seconds: Optional[int] = None
    set_limit_delay_in_seconds_multiple_inverter: Optional[int] = None
    poll_interval_in_seconds: Optional[int] = None
    on_grid_usage_jump_to_limit_percent: Optional[int] = None
    max_difference_between_limit_and_outputpower: Optional[int] = None
    set_limit_retry: Optional[int] = None
    set_power_status_delay_in_seconds: Optional[int] = None

    modhopper1: Optional[int] = None
    modhopper2: Optional[int] = None
    modhopper_key: Optional[str] = None
    modhopper_rf_config: Optional[int] = None
    modhopper_rf_channel: Optional[int] = None
    status: Optional[bool] = None

    logging_interval: Optional[ConfigInformationShort] = None
    logging_interval_list: Optional[list[ConfigInformationShort]] = None
    first_page_on_login: Optional[ScreenBase] = None
    screen_list: Optional[list[ScreenBase]] = None

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
