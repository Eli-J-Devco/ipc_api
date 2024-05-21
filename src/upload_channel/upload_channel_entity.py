# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..config import config


class UploadChannel(config.Base):
    __tablename__ = "upload_channel"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    id_type_protocol: Mapped[int] = mapped_column(Integer,
                                                  ForeignKey("config_information.id",
                                                             ondelete="CASCADE",
                                                             onupdate="CASCADE"),
                                                  nullable=False)
    id_type_logging_interval: Mapped[int] = mapped_column(Integer,
                                                          ForeignKey("config_information.id",
                                                                     ondelete="CASCADE",
                                                                     onupdate="CASCADE"),
                                                          nullable=False)
    uploadurl: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=True)
    password: Mapped[str] = mapped_column(String, nullable=True)
    selected_upload: Mapped[str] = mapped_column(String, nullable=True)
    enable: Mapped[bool] = mapped_column(Integer, nullable=False)
    allow_remote_configuration: Mapped[bool] = mapped_column(Integer, nullable=False)
    status: Mapped[bool] = mapped_column(Integer, nullable=False)

    type_protocol = relationship("ConfigInformation", foreign_keys=[id_type_protocol])
    logging_interval = relationship("ConfigInformation", foreign_keys=[id_type_logging_interval])


class UploadChannelDeviceMap(config.Base):
    __tablename__ = "upload_channel_device_map"

    id_upload_channel: Mapped[int] = mapped_column(Integer,
                                                   ForeignKey("upload_channel.id",
                                                              ondelete="CASCADE",
                                                              onupdate="CASCADE"),
                                                   primary_key=True)
    id_device: Mapped[int] = mapped_column(Integer,
                                           ForeignKey("device_list.id",
                                                      ondelete="CASCADE",
                                                      onupdate="CASCADE"),
                                           primary_key=True)
