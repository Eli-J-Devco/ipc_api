# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from sqlalchemy import Integer, String, DOUBLE, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..config import config
from ..point_config.point_config_filter import PointType


class Point(config.Base):
    __tablename__ = "point_list"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent: Mapped[int] = mapped_column(Integer, ForeignKey("point_list.id"), nullable=False)
    id_pointclass_type: Mapped[int] = mapped_column(Integer, ForeignKey("pointclass_type.id", ondelete="CASCADE",
                                                                        onupdate="CASCADE"), nullable=True, default=1)
    id_pointkey: Mapped[int] = mapped_column(Integer, nullable=False)
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
    id_pointtype: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
                                                                  onupdate="CASCADE"), nullable=True)
    id_config_information: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
                                                                           onupdate="CASCADE"), nullable=True,
                                                       default=PointType().POINT)
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

    template_library = relationship("Template", back_populates="point_list", foreign_keys=[id_template])
    type_units = relationship("ConfigInformation", foreign_keys=[id_type_units], lazy="immediate")
    type_datatype = relationship("ConfigInformation", foreign_keys=[id_type_datatype], lazy="immediate")
    type_byteorder = relationship("ConfigInformation", foreign_keys=[id_type_byteorder], lazy="immediate")
    type_point_list = relationship("PointListType", foreign_keys=[id_point_list_type], lazy="immediate")
    type_point = relationship("ConfigInformation", foreign_keys=[id_pointtype], lazy="immediate")
    type_class = relationship("PointclassType", foreign_keys=[id_pointclass_type], lazy="immediate")
    type_config_information = relationship("ConfigInformation", foreign_keys=[id_config_information], lazy="immediate")
    type_control = relationship("PointListControlGroup", foreign_keys=[id_control_group], lazy="immediate")
    type_function = relationship("ConfigInformation", foreign_keys=[id_type_function], lazy="immediate")
    reply_to_point = relationship("Point", remote_side=[parent])


class ManualPoint(config.Base):
    __tablename__ = "manual_point_list"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent: Mapped[int] = mapped_column(Integer, ForeignKey("point_list.id"), nullable=False)
    id_device_type: Mapped[int] = mapped_column(Integer,
                                                ForeignKey("device_type.id", ondelete="CASCADE", onupdate="CASCADE"),
                                                nullable=True)
    id_pointclass_type: Mapped[int] = mapped_column(Integer, ForeignKey("pointclass_type.id", ondelete="CASCADE",
                                                                        onupdate="CASCADE"), nullable=True, default=1)
    id_pointkey: Mapped[int] = mapped_column(Integer, nullable=False)
    id_point_list_type: Mapped[int] = mapped_column(Integer, ForeignKey("point_list_type.id", ondelete="CASCADE",
                                                                        onupdate="CASCADE"), nullable=False, default=1)
    name: Mapped[str] = mapped_column(String, nullable=False)
    nameedit: Mapped[bool] = mapped_column(Integer, nullable=False, default=True)
    id_type_units: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
                                                                   onupdate="CASCADE"), nullable=True)
    unitsedit: Mapped[bool] = mapped_column(Integer, nullable=False, default=True)
    id_pointtype: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
                                                                  onupdate="CASCADE"), nullable=True)
    id_config_information: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
                                                                           onupdate="CASCADE"), nullable=True)
    register: Mapped[int] = mapped_column(Integer, nullable=False)
    id_type_datatype: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
                                                                      onupdate="CASCADE"), nullable=False, default=4)
    id_type_byteorder: Mapped[int] = mapped_column(Integer, ForeignKey("config_information.id", ondelete="CASCADE",
                                                                       onupdate="CASCADE"), nullable=False, default=252)
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

    device_type = relationship("DeviceType", foreign_keys=[id_device_type])
    type_units = relationship("ConfigInformation", foreign_keys=[id_type_units], lazy="immediate")
    type_datatype = relationship("ConfigInformation", foreign_keys=[id_type_datatype], lazy="immediate")
    type_byteorder = relationship("ConfigInformation", foreign_keys=[id_type_byteorder], lazy="immediate")
    type_point_list = relationship("PointListType", foreign_keys=[id_point_list_type], lazy="immediate")
    type_point = relationship("ConfigInformation", foreign_keys=[id_pointtype], lazy="immediate")
    type_class = relationship("PointclassType", foreign_keys=[id_pointclass_type], lazy="immediate")
    type_config_information = relationship("ConfigInformation", foreign_keys=[id_config_information], lazy="immediate")
    type_control = relationship("PointListControlGroup", foreign_keys=[id_control_group], lazy="immediate")
    reply_to_point = relationship("Point", remote_side=[parent])
