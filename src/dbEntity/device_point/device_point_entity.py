# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from sqlalchemy import DOUBLE, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.config import orm_provider as config


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

    point_list = relationship("Point",
                              foreign_keys=[id_point_list],
                              lazy="immediate")
