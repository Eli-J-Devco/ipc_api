from sqlalchemy import INTEGER, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .config import orm_provider as config


class ProjectSetup(config.Base):
    __tablename__ = "project_setup"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    serial_number: Mapped[str] = mapped_column(String(255), nullable=True)


class ConfigInformation(config.Base):
    __tablename__ = "config_information"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)


class PointList(config.Base):
    __tablename__ = "point_list"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    parent: Mapped[int] = mapped_column(INTEGER, nullable=True)
    id_pointkey: Mapped[String] = mapped_column(String(255), unique=True)
    id_template: Mapped[int] = mapped_column(INTEGER, ForeignKey("template_library.id",
                                                                 ondelete="CASCADE",
                                                                 onupdate="CASCADE"),
                                             nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    id_config_information: Mapped[int] = mapped_column(INTEGER, ForeignKey("config_information.id",
                                                                           ondelete="CASCADE",
                                                                           onupdate="CASCADE"),
                                                       nullable=True)
    status: Mapped[int] = mapped_column(INTEGER, nullable=True)


class TemplateLibrary(config.Base):
    __tablename__ = "template_library"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)


class Communication(config.Base):
    __tablename__ = "communication"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class Devices(config.Base):
    __tablename__ = "device_list"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    table_name: Mapped[str] = mapped_column(String(255), unique=True)
    view_table: Mapped[str] = mapped_column(String(255), unique=True)
    id_template: Mapped[int] = mapped_column(INTEGER, ForeignKey("template_library.id",
                                                                 ondelete="SET NULL",
                                                                 onupdate="SET NULL"),
                                             nullable=True)
    id_communication: Mapped[int] = mapped_column(INTEGER, ForeignKey("communication.id",
                                                                      ondelete="CASCADE",
                                                                      onupdate="CASCADE"),
                                                  nullable=True)

    communication = relationship("Communication", backref="device_list", foreign_keys=[id_communication], lazy="immediate")


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
    id_device_mppt: Mapped[int] = mapped_column(INTEGER, ForeignKey("device_mppt.id",
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
    id_device_string: Mapped[int] = mapped_column(INTEGER, ForeignKey("device_mppt_string.id",
                                                                      ondelete="CASCADE",
                                                                      onupdate="CASCADE"),
                                                  nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=True)


class DevicePointListMap(config.Base):
    __tablename__ = "device_point_list_map"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    id_device_list: Mapped[int] = mapped_column(INTEGER, ForeignKey("device_list.id",
                                                                    ondelete="CASCADE",
                                                                    onupdate="CASCADE"),
                                                nullable=False)
    id_point_list: Mapped[int] = mapped_column(INTEGER, ForeignKey("point_list.id",
                                                                   ondelete="CASCADE",
                                                                   onupdate="CASCADE"),
                                               nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
