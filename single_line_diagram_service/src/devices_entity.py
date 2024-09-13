from sqlalchemy import INTEGER, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .config import orm_provider as config


# class PointList(config.Base):
#     __tablename__ = "point_list"
#
#     id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
#     parent: Mapped[int] = mapped_column(INTEGER, nullable=True)
#     id_pointkey: Mapped[String] = mapped_column(String(255), unique=True)
#     id_template: Mapped[int] = mapped_column(INTEGER, ForeignKey("template_library.id",
#                                                                  ondelete="CASCADE",
#                                                                  onupdate="CASCADE"),
#                                              nullable=True)
#     name: Mapped[str] = mapped_column(String(255), nullable=True)
#     id_config_information: Mapped[int] = mapped_column(INTEGER, ForeignKey("config_information.id",
#                                                                            ondelete="CASCADE",
#                                                                            onupdate="CASCADE"),
#                                                        nullable=True)
#     id_control_group: Mapped[int] = mapped_column(INTEGER, nullable=True)
#     status: Mapped[int] = mapped_column(INTEGER, nullable=True)
#
#     config_information = relationship("ConfigInformation", backref="point_list", lazy="immediate")


class TemplateLibrary(config.Base):
    __tablename__ = "template_library"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)


class ProjectSetup(config.Base):
    __tablename__ = "project_setup"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    serial_number: Mapped[str] = mapped_column(String(255), nullable=True)


class Communication(config.Base):
    __tablename__ = "communication"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    id_driver_list: Mapped[int] = mapped_column(INTEGER, nullable=False)


class DeviceType(config.Base):
    __tablename__ = "device_type"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    type: Mapped[int] = mapped_column(INTEGER, nullable=True)


class Devices(config.Base):
    __tablename__ = "device_list"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    parent: Mapped[int] = mapped_column(INTEGER, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    id_communication: Mapped[int] = mapped_column(INTEGER, ForeignKey("communication.id",
                                                                      ondelete="CASCADE",
                                                                      onupdate="CASCADE"),
                                                  nullable=True)
    id_device_type: Mapped[int] = mapped_column(INTEGER, ForeignKey("device_type.id",
                                                                    ondelete="CASCADE",
                                                                    onupdate="CASCADE"),
                                                nullable=True)
    id_template: Mapped[int] = mapped_column(INTEGER, nullable=True)
    mode: Mapped[int] = mapped_column(INTEGER, nullable=True)
    inverter_type: Mapped[int] = mapped_column(INTEGER, nullable=True)
    plug_point: Mapped[int] = mapped_column(INTEGER, nullable=True)
    status: Mapped[int] = mapped_column(INTEGER, nullable=True)

    communication = relationship("Communication", backref="device_list",
                                 foreign_keys=[id_communication], lazy="immediate")
    device_type = relationship("DeviceType", backref="device_list",
                               foreign_keys=[id_device_type], lazy="immediate")


class DeviceConnection(config.Base):
    __tablename__ = "device_connection"

    device_list_id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    device_table: Mapped[str] = mapped_column(String, primary_key=True)
    connect_device_id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    connect_device_table: Mapped[str] = mapped_column(String, primary_key=True)
    type: Mapped[int] = mapped_column(INTEGER, ForeignKey("device_connection_type.id",
                                                          ondelete="CASCADE",
                                                          onupdate="CASCADE"))

    connection_type = relationship("DeviceConnectionType", foreign_keys=[type])


class DeviceConnectionType(config.Base):
    __tablename__ = "device_connection_type"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    type: Mapped[int] = mapped_column(INTEGER)
    detail_type: Mapped[int] = mapped_column(INTEGER)
    description: Mapped[str] = mapped_column(String, nullable=True)


class DeviceMppt(config.Base):
    __tablename__ = "device_mppt"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    id_device_list: Mapped[int] = mapped_column(INTEGER, ForeignKey("device_list.id",
                                                                    ondelete="CASCADE",
                                                                    onupdate="CASCADE"),
                                                nullable=False)
    id_point_list: Mapped[int] = mapped_column(INTEGER, ForeignKey("point_list.id",
                                                                   ondelete="CASCADE",
                                                                   onupdate="CASCADE"),
                                               nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    namekey: Mapped[str] = mapped_column(String(255), nullable=True)


class DeviceMpptString(config.Base):
    __tablename__ = "device_mppt_string"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    id_device_list: Mapped[int] = mapped_column(INTEGER, ForeignKey("device_list.id",
                                                                    ondelete="CASCADE",
                                                                    onupdate="CASCADE"),
                                                nullable=False)
    id_point_list: Mapped[int] = mapped_column(INTEGER, ForeignKey("point_list.id",
                                                                   ondelete="CASCADE",
                                                                   onupdate="CASCADE"),
                                               nullable=False)
    parent: Mapped[int] = mapped_column(INTEGER, ForeignKey("device_mppt.id",
                                                            ondelete="CASCADE",
                                                            onupdate="CASCADE"),
                                        nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    namekey: Mapped[str] = mapped_column(String(255), nullable=True)
    panel: Mapped[int] = mapped_column(INTEGER, nullable=True)


class DevicePanel(config.Base):
    __tablename__ = "device_panel"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    id_device_list: Mapped[int] = mapped_column(INTEGER, ForeignKey("device_list.id",
                                                                    ondelete="CASCADE",
                                                                    onupdate="CASCADE"),
                                                nullable=False)
    id_point_list: Mapped[int] = mapped_column(INTEGER, ForeignKey("point_list.id",
                                                                   ondelete="CASCADE",
                                                                   onupdate="CASCADE"),
                                               nullable=False)
    parent: Mapped[int] = mapped_column(INTEGER, ForeignKey("device_mppt_string.id",
                                                            ondelete="CASCADE",
                                                            onupdate="CASCADE"),
                                        nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
