# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from sqlalchemy import DOUBLE, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from configs.config import orm_provider as config

class Point(config.Base):
    __tablename__ = "point_list"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent: Mapped[int] = mapped_column(Integer, ForeignKey("point_list.id"), nullable=False)
    id_pointclass_type: Mapped[int] = mapped_column(Integer, ForeignKey("pointclass_type.id", ondelete="CASCADE",
                                                                        onupdate="CASCADE"), nullable=True, default=1)
    id_pointkey: Mapped[int] = mapped_column(Integer, nullable=False)
    alias: Mapped[str] = mapped_column(String, nullable=False)
    id_template: Mapped[int] = mapped_column(Integer,
                                             ForeignKey("template_library.id", ondelete="CASCADE", onupdate="CASCADE"),
                                             nullable=False)
    id_point_list_type: Mapped[int] = mapped_column(Integer, ForeignKey("point_list_type.id", ondelete="CASCADE",
                                                                        onupdate="CASCADE"), nullable=False, default=1)
    name: Mapped[str] = mapped_column(String, nullable=False)
    nameedit: Mapped[bool] = mapped_column(Integer, nullable=False, default=False)
    id_type_units: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
                                                                   onupdate="CASCADE"), nullable=True)
    unitsedit: Mapped[bool] = mapped_column(Integer, nullable=False, default=False)
    # id_pointtype: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
    #                                                               onupdate="CASCADE"), nullable=True)
    # id_config_information: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
    #                                                                        onupdate="CASCADE"), nullable=True,
    #                                                    default=PointType().POINT)
    register: Mapped[int] = mapped_column(Integer, nullable=False)
    id_type_datatype: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
                                                                      onupdate="CASCADE"), nullable=False, default=4)
    id_type_byteorder: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
                                                                       onupdate="CASCADE"), nullable=False, default=252)
    id_type_function: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
                                                                      onupdate="CASCADE"), nullable=True, default=269)
    slope: Mapped[float] = mapped_column(DOUBLE, nullable=False)
    slopeenabled: Mapped[bool] = mapped_column(Integer, nullable=False, default=False)
    offset: Mapped[float] = mapped_column(DOUBLE, nullable=False)
    offsetenabled: Mapped[bool] = mapped_column(Integer, nullable=False, default=False)
    multreg: Mapped[int] = mapped_column(Integer, nullable=False)
    multregenabled: Mapped[bool] = mapped_column(Integer, nullable=True, default=False)
    userscaleenabled: Mapped[bool] = mapped_column(Integer, nullable=False, default=False)
    invalidvalue: Mapped[int] = mapped_column(Integer, nullable=False)
    invalidvalueenabled: Mapped[bool] = mapped_column(Integer, nullable=False, default=False)
    id_control_group: Mapped[int] = mapped_column(Integer, ForeignKey("point_list_control_group.id", ondelete="CASCADE",
                                                                      onupdate="CASCADE"), nullable=True)
    extendednumpoints: Mapped[int] = mapped_column(Integer, nullable=True)
    extendedregblocks: Mapped[int] = mapped_column(Integer, nullable=True)
    function: Mapped[str] = mapped_column(String, nullable=True)
    constants: Mapped[str] = mapped_column(String, nullable=True, default=0)
    active: Mapped[bool] = mapped_column(Integer, nullable=False, default=True)
    status: Mapped[bool] = mapped_column(Integer, nullable=False, default=True)

    control_type_input: Mapped[int] = mapped_column(Integer, nullable=True)