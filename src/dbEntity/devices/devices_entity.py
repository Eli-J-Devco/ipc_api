# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy import DOUBLE, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.config import orm_provider as config


class Devices(config.Base):
    __tablename__ = "device_list"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent: Mapped[int] = mapped_column(Integer, nullable=True)
    table_name: Mapped[str] = mapped_column(String, unique=True)
    view_table: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    device_virtual: Mapped[bool] = mapped_column(Integer, nullable=True)
    id_project_setup: Mapped[int] = mapped_column(Integer, ForeignKey("project_setup.id",
                                                                      ondelete="CASCADE",
                                                                      onupdate="CASCADE"),
                                                  nullable=True)
    id_device_type: Mapped[int] = mapped_column(Integer,
                                                ForeignKey("device_type.id",
                                                           ondelete="CASCADE",
                                                           onupdate="CASCADE"),
                                                nullable=True)
    id_communication: Mapped[int] = mapped_column(Integer, ForeignKey("communication.id",
                                                                      ondelete="CASCADE",
                                                                      onupdate="CASCADE"),
                                                  nullable=True)
    id_template: Mapped[int] = mapped_column(Integer, ForeignKey("template_library.id",
                                                                 ondelete="CASCADE",
                                                                 onupdate="CASCADE"),
                                             nullable=True)
    rtu_bus_address: Mapped[int] = mapped_column(Integer, nullable=True)
    tcp_gateway_ip: Mapped[str] = mapped_column(String, nullable=True)
    tcp_gateway_port: Mapped[int] = mapped_column(Integer, nullable=True)
    enable: Mapped[bool] = mapped_column(Integer, nullable=True)

    rated_power: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    rated_power_custom: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    min_watt_in_percent: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    DC_voltage: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    DC_current: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    compensate_watt_factor: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    battery_mode: Mapped[int] = mapped_column(Integer, nullable=True)
    battery_normal_watt: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    battery_reduce_watt: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    battery_threshold_off_limit_in_v: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    battery_threshold_reduce_limit_in_v: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    battery_threshold_normal_limit_in_v: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    battery_threshold_on_limit_in_v: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    battery_priority: Mapped[int] = mapped_column(Integer, nullable=True)

    point: Mapped[int] = mapped_column(Integer, nullable=True)
    pv: Mapped[int] = mapped_column(Integer, nullable=True)
    mode: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    model: Mapped[int] = mapped_column(Integer, nullable=True)
    function: Mapped[int] = mapped_column(Integer, nullable=True)
    point_p: Mapped[int] = mapped_column(Integer,
                                         ForeignKey("point_list.id",
                                                    ondelete="SET NULL",
                                                    onupdate="SET NULL"),
                                         nullable=True)
    value_p: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    send_p: Mapped[int] = mapped_column(Integer, nullable=True)

    point_q: Mapped[int] = mapped_column(Integer,
                                         ForeignKey("point_list.id",
                                                    ondelete="SET NULL",
                                                    onupdate="SET NULL"),
                                         nullable=True)
    value_q: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    send_q: Mapped[int] = mapped_column(Integer, nullable=True)

    point_pf: Mapped[int] = mapped_column(Integer,
                                          ForeignKey("point_list.id",
                                                     ondelete="SET NULL",
                                                     onupdate="SET NULL"),
                                          nullable=True)
    value_pf: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    send_pf: Mapped[int] = mapped_column(Integer, nullable=True)

    max: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    efficiency: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    allow_error: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    enable_poweroff: Mapped[int] = mapped_column(Integer, nullable=True)
    inverter_shutdown: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    meter_type: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    inverter_type: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    creation_state: Mapped[int] = mapped_column(Integer, nullable=True, default=-1)
    status: Mapped[bool] = mapped_column(Integer, nullable=True, default=True)

    # communication = relationship("Rs485", foreign_keys=[id_communication], lazy="immediate")
    device_type = relationship("DeviceType", foreign_keys=[id_device_type], lazy="immediate")
    # project_setup = relationship("ProjectSetup", foreign_keys=[id_project_setup])
    # template = relationship("Template", foreign_keys=[id_template], lazy="immediate")
    # point_list_p = relationship("Point", foreign_keys=[point_p])
    # point_list_q = relationship("Point", foreign_keys=[point_q])
    # point_list_pf = relationship("Point", foreign_keys=[point_pf])


class DeviceType(config.Base):
    __tablename__ = "device_type"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    status: Mapped[bool] = mapped_column(Integer, nullable=True)
    type: Mapped[int] = mapped_column(Integer, nullable=True)


class DeviceGroup(config.Base):
    __tablename__ = "device_group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    id_device_type: Mapped[int] = mapped_column(Integer,
                                                ForeignKey("device_type.id",
                                                           ondelete="CASCADE",
                                                           onupdate="CASCADE"),
                                                nullable=True)
    status: Mapped[bool] = mapped_column(Integer, nullable=True, default=True)
    type: Mapped[bool] = mapped_column(Integer, nullable=True)

    device_type = relationship("DeviceType", foreign_keys=[id_device_type])


class DeviceComponent(config.Base):
    __tablename__ = "device_component"
    main_type: Mapped[int] = mapped_column(Integer,
                                           ForeignKey("device_type.id",
                                                               ondelete="RESTRICT",
                                                               onupdate="RESTRICT"),
                                           primary_key=True,
                                           nullable=False)
    sub_type: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=True)
    component: Mapped[int] = mapped_column(Integer, ForeignKey("device_type.id",
                                                               ondelete="RESTRICT",
                                                               onupdate="RESTRICT"),
                                           primary_key=True,
                                           nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=True)

    main_device_type = relationship("DeviceType", foreign_keys=[main_type], lazy="immediate")
    component_type = relationship("DeviceType", foreign_keys=[component], lazy="immediate")
class DevicePointMap(config.Base):
    __tablename__ = "device_point_list_map"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_device_list: Mapped[int] = mapped_column(Integer, ForeignKey("device_list.id",
                                                                    ondelete="CASCADE",
                                                                    onupdate="CASCADE"),
                                                nullable=True)
    id_point_list: Mapped[int] = mapped_column(Integer, ForeignKey("point_list.id",
                                                                   ondelete="CASCADE",
                                                                   onupdate="CASCADE"),
                                               nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    low_alarm: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    high_alarm: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    output_values: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    status: Mapped[bool] = mapped_column(Integer, nullable=True)
class DeviceMPPT(config.Base):
    __tablename__ = "device_mppt"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    id_device_list: Mapped[int] = mapped_column(Integer, ForeignKey("device_list.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    id_point_list: Mapped[int] = mapped_column(Integer, ForeignKey("point_list.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    namekey: Mapped[str] = mapped_column(String(255), nullable=True)
    voltage: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    current: Mapped[float] = mapped_column(DOUBLE, nullable=True)


    # Relationships
    device = relationship("Devices", foreign_keys=[id_device_list], lazy="immediate")
    # point = relationship("PointList", foreign_keys=[id_point_list], lazy="immediate")

class DeviceMPPTString(config.Base):
    __tablename__ = "device_mppt_string"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    id_device_list: Mapped[int] = mapped_column(Integer, ForeignKey("device_list.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    id_point_list: Mapped[int] = mapped_column(Integer, ForeignKey("point_list.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    id_device_mppt: Mapped[int] = mapped_column(Integer, ForeignKey("device_mppt.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    namekey: Mapped[str] = mapped_column(String(255), nullable=True)
    panel: Mapped[int] = mapped_column(Integer, nullable=True)
    current: Mapped[float] = mapped_column(DOUBLE, nullable=True)
    # Relationships
    device = relationship("Devices", foreign_keys=[id_device_list], lazy="immediate")
    # point = relationship("PointList", foreign_keys=[id_point_list], lazy="immediate")
    device_mppt = relationship("DeviceMPPT", foreign_keys=[id_device_mppt], lazy="immediate")