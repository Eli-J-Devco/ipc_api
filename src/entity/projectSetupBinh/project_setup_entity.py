# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime
from sqlalchemy import DATETIME, DOUBLE, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from configs.config import DBSessionManager

class ProjectSetup(DBSessionManager.Base):
    __tablename__ = "project_setup"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    serial_number: Mapped[str] = mapped_column(String, unique=True)
    location: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    administrative_contact: Mapped[str] = mapped_column(String, nullable=True)
    # id_first_page_on_login: Mapped[int] = mapped_column(Integer,
    #                                                         ForeignKey("screen.id", ondelete="CASCADE", onupdate="CASCADE"),
    #                                                         nullable=False)
    id_logging_interval: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
                                                            onupdate="CASCADE"), nullable=False)
    id_scheduled_upload_time: Mapped[int] = mapped_column(Integer,
                                                            ForeignKey("config_information.id", ondelete="CASCADE",
                                                            onupdate="CASCADE"), nullable=False)
    # number_times_retry: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    id_time_wait_before_retry: Mapped[int] = mapped_column(Integer,
                                                            ForeignKey("config_information.id", ondelete="CASCADE",
                                                            onupdate="CASCADE"), nullable=False)
    # id_upload_debug_information: Mapped[int] = mapped_column(Integer,
    #                                                         ForeignKey("config_information.id", ondelete="CASCADE",
    #                                                         onupdate="CASCADE"), nullable=False)
    enable_upload_data_on_alarm_status: Mapped[bool] = mapped_column(Integer, nullable=False, default=True)
    enable_upload_data_on_low_disk: Mapped[bool] = mapped_column(Integer, nullable=False, default=True)
    enable_upload_data_on_system_startup: Mapped[bool] = mapped_column(Integer, nullable=False, default=True)
    link_remote_access: Mapped[str] = mapped_column(String, nullable=True)
    allow_remote_access: Mapped[bool] = mapped_column(Integer, nullable=False, default=True)
    enable_static_routing: Mapped[bool] = mapped_column(Integer, nullable=False, default=True)
    mode: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # id_time_zone: Mapped[int] = mapped_column(Integer,ForeignKey("time_zone.id", ondelete="CASCADE", onupdate="CASCADE"),
    #                                                         nullable=False)
    Time1cycle: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
    sampling_time1cycle: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
    control_mode: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    value_offset_zero_export: Mapped[float] = mapped_column(DOUBLE, nullable=False, default=100)
    threshold_zero_export= mapped_column(DOUBLE, nullable=False, default=0)
    value_power_limit: Mapped[float] = mapped_column(DOUBLE, nullable=False, default=100)
    value_offset_power_limit: Mapped[float] = mapped_column(DOUBLE, nullable=False, default=0)
    kp_zero_export= mapped_column(DOUBLE, nullable=False, default=1)
    ki_zero_export= mapped_column(DOUBLE, nullable=False, default=0.1)
    kd_zero_export= mapped_column(DOUBLE, nullable=False, default=0)
    delta_time_zero_export= mapped_column(DOUBLE, nullable=False, default=1)
    kp_power_limit= mapped_column(DOUBLE, nullable=False, default=1)
    ki_power_limit= mapped_column(DOUBLE, nullable=False, default=0.1)
    kd_power_limit= mapped_column(DOUBLE, nullable=False, default=0)
    delta_time_power_limit= mapped_column(DOUBLE, nullable=False, default=1)
    value_zero_export: Mapped[float] = mapped_column(DOUBLE, nullable=False, default=100)
    enable_power_limit: Mapped[bool] = mapped_column(Integer, nullable=False, default=False)
    powermeter_target_point: Mapped[float] = mapped_column(DOUBLE, nullable=False, default=0)
    enable_zero_export: Mapped[bool] = mapped_column(Integer, nullable=False, default=False)
    powermeter_tolerance: Mapped[float] = mapped_column(DOUBLE, nullable=False, default=0)
    powermeter_max_point: Mapped[float] = mapped_column(DOUBLE, nullable=False, default=0)
    slow_approx_limit_in_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    slow_approx_factor_in_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    loop_interval_in_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    set_limit_delay_in_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    set_limit_timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    set_limit_delay_in_seconds_multiple_inverter: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    poll_interval_in_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    on_grid_usage_jump_to_limit_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_difference_between_limit_and_outputpower: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    set_limit_retry: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    set_power_status_delay_in_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    enable_search_modbus_rtu_device: Mapped[bool] = mapped_column(Integer, nullable=False, default=0)
    modhopper1: Mapped[int] = mapped_column(Integer, nullable=True)
    modhopper2: Mapped[int] = mapped_column(Integer, nullable=True)
    modhopper_key: Mapped[str] = mapped_column(String, nullable=True)
    modhopper_rf_config: Mapped[str] = mapped_column(String, nullable=True)
    modhopper_rf_channel: Mapped[int] = mapped_column(Integer, nullable=True)
    mqtt_broker_cloud: Mapped[str] = mapped_column(String, nullable=True)
    mqtt_port_cloud: Mapped[int] = mapped_column(Integer, nullable=True)
    mqtt_username_cloud: Mapped[str] = mapped_column(String, nullable=True)
    mqtt_password_cloud: Mapped[str] = mapped_column(String, nullable=True)
    low_performance: Mapped[float] = mapped_column(DOUBLE, nullable=False, default=50)
    high_performance: Mapped[float] = mapped_column(DOUBLE, nullable=False, default=100)
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    logging_interval = relationship('ConfigInformation', foreign_keys=[id_logging_interval])
#     first_page_on_login = relationship('Screen', foreign_keys=[id_first_page_on_login])
#     scheduled_upload_time = relationship('ConfigInformation', foreign_keys=[id_scheduled_upload_time])
#     time_wait_before_retry = relationship('ConfigInformation', foreign_keys=[id_time_wait_before_retry])
#     upload_debug_information = relationship('ConfigInformation', foreign_keys=[id_upload_debug_information])
#     time_zone = relationship('TimeZone', foreign_keys=[id_time_zone])

class ConfigInformation(DBSessionManager.Base):
    __tablename__ = "config_information"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent: Mapped[str] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    namekey: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    value: Mapped[str] = mapped_column(Integer, nullable=True)
    type: Mapped[str] = mapped_column(Integer, nullable=True)
    id_type: Mapped[int] = mapped_column(Integer, ForeignKey("config_type.id", ondelete="CASCADE", onupdate="CASCADE"),
                                        nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    id_pointclass_type: Mapped[int] = mapped_column(Integer, ForeignKey("pointclass_type.id", ondelete="CASCADE",
                                                                        onupdate="CASCADE"), nullable=False)

    config_type = relationship("ConfigType", foreign_keys=[id_type])
    # pointclass_type = relationship("PointclassType", foreign_keys=[id_pointclass_type])


class ConfigType(DBSessionManager.Base):
    __tablename__ = "config_type"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)


# class TimeZone(DBSessionManager.Base):
#     __tablename__ = "time_zone"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
#     namekey: Mapped[str] = mapped_column(String, unique=True, nullable=False)
#     status: Mapped[int] = mapped_column(Integer, nullable=False)


# class Screen(DBSessionManager.Base):
#     __tablename__ = "screen"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     screen_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
#     description: Mapped[str] = mapped_column(String, nullable=True)
#     status: Mapped[int] = mapped_column(Integer, nullable=False)
#     class_icon: Mapped[str] = mapped_column(String, nullable=True)
#     level: Mapped[int] = mapped_column(Integer, nullable=False)
#     parent: Mapped[int] = mapped_column(Integer, nullable=True)
#     path: Mapped[str] = mapped_column(String, nullable=True)
#     has_child: Mapped[bool] = mapped_column(Integer, nullable=False)
#     created_date: Mapped[datetime.datetime] = mapped_column(DATETIME, nullable=True)
#     updated_date: Mapped[datetime.datetime] = mapped_column(DATETIME, nullable=True)
#     created_by: Mapped[str] = mapped_column(String, nullable=True)
#     updated_by: Mapped[str] = mapped_column(String, nullable=True)
#     show_menu: Mapped[bool] = mapped_column(Integer, nullable=False)


# class Page(DBSessionManager.Base):
#     __tablename__ = "page"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(String, nullable=False)
#     description: Mapped[str] = mapped_column(String, nullable=True)
#     status: Mapped[int] = mapped_column(Integer, nullable=True)
