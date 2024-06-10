# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func, insert, join, literal_column, select, text

from configs.config import orm_provider as db_config


class SldGroup(db_config.Base):
    __tablename__ = "sld_group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[bool] = mapped_column(Integer, nullable=False)
# class SldGroupInv(db_config.Base):
#     __tablename__ = "sld_group_inv"

#     id_sld_group: Mapped[int] = mapped_column(Integer, 
#                                               ForeignKey("sld_group.id",
#                                                              ondelete="CASCADE",
#                                                              onupdate="CASCADE"), 
#                                               nullable=False)
#     id_device_list: Mapped[int] = mapped_column(Integer, 
#                                               ForeignKey("device_list.id",
#                                                              ondelete="CASCADE",
#                                                              onupdate="CASCADE"), 
#                                               nullable=False)
#     status: Mapped[bool] = mapped_column(Boolean, nullable=False)
#     sld_group = relationship("SldGroup", foreign_keys=[id_sld_group])
#     device_list = relationship("Device_list", foreign_keys=[id_device_list])
    
# class SLD_GROUP_METER(db_config.Base):
#     __tablename__ = "sld_group_meter"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
#     name: Mapped[str] = mapped_column(String(255), nullable=False)
#     type: Mapped[int] = mapped_column(Integer, nullable=False)
#     status: Mapped[bool] = mapped_column(Integer, nullable=False)