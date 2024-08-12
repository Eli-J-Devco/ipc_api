# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.config import orm_provider as config


class Rs485(config.Base):
    __tablename__ = "communication"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    namekey: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    id_driver_list: Mapped[int] = mapped_column(Integer,
                                                ForeignKey("driver_list.id", ondelete="CASCADE", onupdate="CASCADE"),
                                                nullable=True)
    id_type_baud_rates: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
                                                                        onupdate="CASCADE"), nullable=True)
    id_type_parity: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
                                                                    onupdate="CASCADE"), nullable=True)
    id_type_stopbits: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
                                                                      onupdate="CASCADE"), nullable=True)
    id_type_timeout: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
                                                                     onupdate="CASCADE"), nullable=True)
    id_type_debug_level: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
                                                                         onupdate="CASCADE"), nullable=True)
    note1: Mapped[str] = mapped_column(String, nullable=True)
    note2: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[bool] = mapped_column(Integer, nullable=True)

    driver_list = relationship("DriverList", foreign_keys=[id_driver_list])


class DriverList(config.Base):
    __tablename__ = "driver_list"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[bool] = mapped_column(Integer, nullable=True)
