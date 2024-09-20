from pydantic import BaseModel
from typing import Optional
class ProjectSetupModel(BaseModel):
    id: int
    name: str
    serial_number: str
    location: str
    description: str
    administrative_contact: str
    enable_upload_data_on_alarm_status: bool
    enable_upload_data_on_low_disk: bool
    enable_upload_data_on_system_startup: bool
    link_remote_access: str
    allow_remote_access: bool
    enable_static_routing: bool
    mode: str
    Time1cycle: int
    sampling_time1cycle: int
    control_mode: str
    value_offset_zero_export: Optional[float] = None
    threshold_zero_export: Optional[float] = None
    value_power_limit: Optional[float] = None
    value_offset_power_limit: Optional[float] = None
    kp_zero_export: Optional[float] = None
    ki_zero_export: Optional[float] = None
    kd_zero_export: Optional[float] = None
    delta_time_zero_export: Optional[float] = None
    kp_power_limit: Optional[float] = None
    ki_power_limit: Optional[float] = None
    kd_power_limit: Optional[float] = None
    delta_time_power_limit: Optional[float] = None
    value_zero_export: Optional[float] = None
    enable_power_limit: bool
    powermeter_target_point: Optional[str] = None
    enable_zero_export: bool
    powermeter_tolerance: Optional[float] = None
    powermeter_max_point: Optional[float] = None
    slow_approx_limit_in_percent: Optional[float] = None
    slow_approx_factor_in_percent: Optional[float] = None
    loop_interval_in_seconds: int
    set_limit_delay_in_seconds: int
    set_limit_timeout_seconds: int
    set_limit_delay_in_seconds_multiple_inverter: int
    poll_interval_in_seconds: int
    on_grid_usage_jump_to_limit_percent: Optional[float] = None
    max_difference_between_limit_and_outputpower: Optional[float] = None
    set_limit_retry: int
    set_power_status_delay_in_seconds: int
    enable_search_modbus_rtu_device: bool
    modhopper1: Optional[str] = None
    modhopper2: Optional[str] = None
    modhopper_key: Optional[str] = None
    modhopper_rf_config: Optional[str] = None
    modhopper_rf_channel: Optional[str] = None
    mqtt_broker_cloud: str
    mqtt_port_cloud: int
    mqtt_username_cloud: str
    mqtt_password_cloud: str
    low_performance: int
    high_performance: int
    status: Optional[str] = None

    class Config:
        orm_mode = True