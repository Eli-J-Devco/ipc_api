# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime
import os
import sys
from sqlalchemy import exc
from sqlalchemy.schema import CreateTable

# import logging
from typing import Optional

from fastapi import (
    APIRouter,
    Body,
    Depends,
    status,
)
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from utils.response_msg_helper import formatMessage

sys.path.append(
    (
        lambda project_name: (
            os.path.dirname(__file__)[
                : len(project_name) + os.path.dirname(__file__).find(project_name)
            ]
            if project_name and project_name in os.path.dirname(__file__)
            else -1
        )
    )("src")
)
import api.domain.deviceGroup.models as deviceGroup_models
import api.domain.deviceGroup.schemas as deviceGroup_schemas
import api.domain.deviceList.models as deviceList_models
import api.domain.template.models as template_models
import api.domain.template.schemas as template_schemas
import model.models as models
import model.schemas as schemas
import utils.oauth2 as oauth2
from database.db import get_db
from utils.libCom import cov_xml_sql

# from utils.pm2Manager import (LOGGER, cov_xml_sql,
#                               create_device_group_rs485_run_pm2,
#                               create_program_pm2, delete_program_pm2,
#                               find_program_pm2, get_mybatis, path,
#                               path_directory_relative,
#   restart_pm2_change_template,
#                               restart_pm2_update_template, restart_program_pm2,
#                               restart_program_pm2_many)
from utils.pm2Manager import (
    restart_pm2_change_template,
)

# LOGGER = logging.getLogger(__name__)
# # setup root logger
# logger_setup = LoggerSetup()
# # get logger for module
# LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/template", tags=["Template"])


def get_template_by_id(id_template: int, db: Session):
    register_list = []
    point_list = []
    mppt_list = []

    register_query = (
        db.query(models.Register_block)
        .filter(models.Register_block.id_template == id_template)
        .filter(models.Register_block.status == 1)
    )
    register_list = register_query.all()
    #
    point_query = (
        db.query(models.Point_list)
        .filter(models.Point_list.id_template == id_template)
        .filter(models.Point_list.id_config_information == 266)
        .filter(models.Point_list.status == 1)
    )
    point_list = point_query.all()

    mppt_query = (
        db.query(models.Point_list)
        .filter(models.Point_list.id_template == id_template)
        .filter(models.Point_list.id_config_information > 266)
        .filter(models.Point_list.status == 1)
        .order_by(models.Point_list.index.asc())
    ).all()

    for item in mppt_query:
        if item.parent == None:
            if not hasattr(item, "children"):
                item.children = []
            mppt_list.append(item)
        else:
            for mppt in mppt_list:
                if item.parent == mppt.id:
                    mppt.children.append(item)
                    break
                else:
                    for child in mppt.children:
                        if item.parent == child.id:
                            if not hasattr(child, "children"):
                                child.children = []
                            child.children.append(item)
                            break

    return {
        "point_list": point_list,
        "mppt_list": mppt_list,
        "register_list": register_list,
    }


# region Template
# Describe functions before writing code
# 	 * @description create template modbus
# 	 * @author vnguyen
# 	 * @since 15-01-2024
# 	 * @param {template,db}
# 	 * @return data (TemplateOutBase)
@router.post("/create/", response_model=template_schemas.TemplateOutBase)
def create_template(
    template: template_schemas.TemplateCreateBase,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:
        name = template.name
        template_query = (
            db.query(template_models.Template_library)
            .filter(template_models.Template_library.name == name)
            .first()
        )
        if template_query:
            return formatMessage(
                f"Template with name: {name} already exists",
                status.HTTP_406_NOT_ACCEPTABLE,
            )

        new_template = template_models.Template_library(**template.model_dump())
        db.add(new_template)
        db.flush()

        # create device point list
        id_device_type = (
            db.query(deviceGroup_models.Device_group)
            .filter(deviceGroup_models.Device_group.id == template.id_device_group)
            .first()
            .id_device_type
        )
        device_point_list_query = (
            db.query(models.ManualPointList)
            .filter(models.ManualPointList.id_device_type == id_device_type)
            .filter(models.ManualPointList.id_config_information == 266)
        )
        result_device_point_list = device_point_list_query.all()
        db.add_all(
            [
                models.Point_list(
                    **schemas.ManualPointBase(**item.__dict__).model_dump(
                        exclude=["id", "id_device_type"]
                    ),
                    id_template=new_template.id,
                )
                for item in result_device_point_list
            ]
        )

        # create device mppt list
        mppt_list_query = (
            db.query(models.ManualPointList)
            .filter(models.ManualPointList.id_device_type == id_device_type)
            .filter(models.ManualPointList.id_config_information > 266)
        )
        result_mppt_list = mppt_list_query.all()
        mppt_to_add_dict = {}
        for item in result_mppt_list:
            if item.parent == None:
                mppt_to_add_dict[item.id] = item.__dict__
                mppt_to_add_dict[item.id]["children"] = []
            else:
                for key in mppt_to_add_dict.keys():
                    if item.parent == key:
                        mppt_to_add_dict[item.parent]["children"].append(item.__dict__)
                    else:
                        for child in range(len(mppt_to_add_dict[key]["children"])):
                            if (
                                item.parent
                                == mppt_to_add_dict[key]["children"][child]["id"]
                            ):
                                if (
                                    "children"
                                    not in mppt_to_add_dict[key]["children"][child]
                                ):
                                    mppt_to_add_dict[key]["children"][child][
                                        "children"
                                    ] = []
                                mppt_to_add_dict[key]["children"][child][
                                    "children"
                                ].append(item.__dict__)
        for key in mppt_to_add_dict.keys():
            mppt = models.Point_list(
                **schemas.ManualPointBase(**mppt_to_add_dict[key]).model_dump(
                    exclude=["id", "id_device_type"]
                ),
                id_template=new_template.id,
            )
            db.add(mppt)
            db.flush()
            for child in mppt_to_add_dict[key]["children"]:
                mppt_string = models.Point_list(
                    **schemas.ManualPointBase(**child).model_dump(
                        exclude=["id", "id_device_type", "parent"]
                    ),
                    parent=mppt.id,
                    id_template=new_template.id,
                )
                db.add(mppt_string)
                db.flush()
                if "children" in child:
                    for panel in child["children"]:
                        mppt_string_panel = models.Point_list(
                            **schemas.ManualPointBase(**panel).model_dump(
                                exclude=["id", "id_device_type", "parent"]
                            ),
                            parent=mppt_string.id,
                            id_template=new_template.id,
                        )
                        db.add(mppt_string_panel)
                        db.flush()
        db.commit()
        db.refresh(new_template)
        return new_template
    except Exception as err:
        print("Error : ", err)

        # LOGGER.error(f'--- {err} ---')
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        #                     detail=f"Not have data")
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Describe functions before writing code
# 	 * @description edit template
# 	 * @author vnguyen
# 	 * @since 10-01-2024
# 	 * @param {,db}
# 	 * @return data ()
@router.post("/edit/", response_model=template_schemas.TemplateListBase)
def edit_each_template(
    template: template_schemas.TemplateUpdateBase,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:
        id = template.id
        template_query = db.query(template_models.Template_library).filter(
            template_models.Template_library.id == id
        )
        result_template = template_query.first()
        # print(f'template_query: {template_query.first()}')
        if not result_template:
            return formatMessage(
                f"Template with id: {id} does not exist", status.HTTP_404_NOT_FOUND
            )

        update_point_list(id, template.point_list, db)
        update_mppt(id, template.mppt_list, db)
        update_point_list(id, template.register_list, db)
        # template_query.update(template.dict())
        restart_pm2_change_template(id, db)
        db.commit()
        return {
            "point_list": template.point_list,
            "mppt_list": template.mppt_list,
            "register_list": template.register_list,
        }
    except Exception as err:
        print("Error : ", err)
        # LOGGER.error(f'--- {err} ---')
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Describe functions before writing code
# 	 * @description delete template
# 	 * @author vnguyen
# 	 * @since 15-01-2024
# 	 * @param {,db}
# 	 * @return data (TemplateDelete)
@router.post("/delete/", response_model=template_schemas.TemplateDelete)
def delete_template(
    id_template: Optional[int] = Body(embed=True),
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:
        template_query = db.query(template_models.Template_library).filter(
            template_models.Template_library.id == id_template
        )
        result_template = template_query.first()
        if not result_template:
            return formatMessage(
                f"Template with id: {id_template} does not exist",
                status.HTTP_404_NOT_FOUND,
            )

        # verify template is being used by device
        device_list = (
            db.query(deviceList_models.Device_list)
            .filter(deviceList_models.Device_list.id_template == id_template)
            .all()
        )
        if device_list:
            return formatMessage(
                f"Template with id: {id_template} is being used by device",
                status.HTTP_406_NOT_ACCEPTABLE,
            )

        # delete point list
        point_query = (
            db.query(models.Point_list)
            .filter(models.Point_list.id_template == id_template)
            .filter(models.Point_list.status == 1)
        )
        result_point = point_query.all()
        for item in result_point:
            point_query.filter(models.Point_list.id == item.id).delete(
                synchronize_session=False
            )

        # delete register list
        register_query = db.query(models.Register_block).filter(
            models.Register_block.id_template == id_template
        )
        result_register = register_query.all()
        for item in result_register:
            register_query.filter(models.Register_block.id == item.id).delete(
                synchronize_session=False
            )

        template_query.delete(synchronize_session=False)
        db.flush()
        # restart_pm2_update_template(result_device_list,db)
        db.commit()
        return formatMessage("Delete template successfully", status.HTTP_200_OK)
    except Exception as err:
        print(f"Error: {err}")
        # LOGGER.error(f'--- {err} ---')
        db.rollback()
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Describe functions before writing code
# 	 * @description get template list
# 	 * @author vnguyen
# 	 * @since 10-01-2024
# 	 * @param {db}
# 	 * @return data (TemplateBase)
@router.post("/get/all/", response_model=list[template_schemas.TemplateBase])
def get_list(
    db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)
):
    try:
        template_query = db.query(template_models.Template_library)
        result_template = template_query.all()
        if not result_template:
            return formatMessage("Template list empty", status.HTTP_404_NOT_FOUND)
        return result_template
    except Exception as err:
        print("Error : ", err)
        # LOGGER.error(f'--- {err} ---')
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Describe functions before writing code
# 	 * @description get each template
# 	 * @author vnguyen
# 	 * @since 28-12-2023
# 	 * @param {id_template,db}
# 	 * @return data (TemplateListBase)
@router.post("/get/", response_model=template_schemas.TemplateListBase)
def get_each_template(
    id_template: Optional[int] = Body(embed=True),
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:
        template_query = (
            db.query(template_models.Template_library)
            .filter(template_models.Template_library.id == id_template)
            .filter(template_models.Template_library.type == 1)
            .first()
        )
        if not template_query:
            return formatMessage(
                f"Template with id: {id_template} does not exist",
                status.HTTP_404_NOT_FOUND,
            )

        return get_template_by_id(id_template, db)
    except Exception as err:
        print("Error : ", err)
        # LOGGER.error(f'--- {err} ---')
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Describe functions before writing code
# 	 * @description get template list by type
# 	 * @author vnguyen
# 	 * @since 10-01-2024
# 	 * @param {db}
# 	 * @return data (TemplateBase)
@router.post("/get/all/type/", response_model=list[template_schemas.TemplateBase])
def get_list_by_type(
    type: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:
        template_query = db.query(template_models.Template_library).filter(
            template_models.Template_library.type == type
        )
        result_template = template_query.all()
        if not result_template:
            return formatMessage("Template list empty", status.HTTP_404_NOT_FOUND)
        return result_template
    except Exception as err:
        print("Error : ", err)
        # LOGGER.error(f'--- {err} ---')
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# endregion


# region Configuration
# Describe functions before writing code
# 	 * @description get tempalte config information
# 	 * @author vnguyen
# 	 * @since 28-12-2023
# 	 * @param {id_template,db}
# 	 * @return data (TemplateListBase)
@router.post("/config/", response_model=template_schemas.TemplateConfigBase)
def get_template_config(
    db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)
):
    try:
        config_point = (
            db.query(models.Config_information)
            .filter(models.Config_information.status == 1)
            .all()
        )

        type_class = db.query(models.Pointclass_type).all()
        type_point_list = db.query(models.PointListType).all()
        type_control_group = db.query(models.PointListControlGroup).all()
        data_type = [item.__dict__ for item in config_point if item.id_type == 1]
        byte_order = [item.__dict__ for item in config_point if item.id_type == 2]
        point_unit = [item.__dict__ for item in config_point if item.id_type == 3]
        type_point = [item.__dict__ for item in config_point if item.id_type == 15]
        type_function = [item.__dict__ for item in config_point if item.id_type == 5]

        return {
            "data_type": data_type,
            "byte_order": byte_order,
            "point_unit": point_unit,
            "type_point": type_point,
            "type_point_list": type_point_list,
            "type_class": type_class,
            "type_function": type_function,
            "type_control_group": type_control_group,
        }
    except Exception as err:
        print("Error : ", err)
        # LOGGER.error(f'--- {err} ---')
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Describe functions before writing code
# 	 * @description get template type
# 	 * @author vnguyen
# 	 * @since 15-01-2024
# 	 * @param {,db}
# 	 * @return data (TemplateTypeBase)
@router.post("/type/", response_model=list[template_schemas.TemplateTypeBase])
def get_type(
    db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)
):
    try:
        template_type_query = (
            db.query(models.Config_information)
            .filter(models.Config_information.status == 1)
            .filter(models.Config_information.id_type == 16)
            .all()
        )

        if not template_type_query:
            return formatMessage("Template type list empty", status.HTTP_404_NOT_FOUND)

        return template_type_query
    except Exception as err:
        print("Error : ", err)
        # LOGGER.error(f'--- {err} ---')
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Describe functions before writing code
# 	 * @description get manual point list by device type id
# 	 * @author vnguyen
# 	 * @since 28-12-2023
# 	 * @param {id_template,db}
# 	 * @return data (TemplateListBase)
@router.post("/get/manual/", response_model=template_schemas.ManualPointOutBase)
def get_manual_point_list(
    id_device_type: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:
        manual_point_list = (
            db.query(models.ManualPointList)
            .filter(models.ManualPointList.id_device_type == id_device_type)
            .all()
        )

        return {"manual_list": manual_point_list}
    except Exception as err:
        print("Error : ", err)
        # LOGGER.error(f'--- {err} ---')
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Describe functions before writing code
# 	 * @description get template group device
# 	 * @author vnguyen
# 	 * @since 28-12-2023
# 	 * @param {id_device_group,db}
# 	 * @return data (TemplateGroupDeviceOutBase)
@router.post(
    "/device/get/group/", response_model=deviceGroup_schemas.TemplateGroupDeviceOutBase
)
def get_group_device(
    id_device_group: Optional[int] = Body(embed=True),
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:
        id = id_device_group
        device_group_query = (
            db.query(deviceGroup_models.Device_group)
            .filter(deviceGroup_models.Device_group.id == id)
            .first()
        )
        if not device_group_query:
            return formatMessage(
                f"Device group with id: {id} does not exist", status.HTTP_404_NOT_FOUND
            )
        # print(device_group_query.__dict__)
        config_point = (
            db.query(models.Config_information)
            .filter(models.Config_information.status == 1)
            .all()
        )
        data_type = []
        data_type = [item.__dict__ for item in config_point if item.id_type == 1]
        byte_order = []
        byte_order = [item.__dict__ for item in config_point if item.id_type == 2]
        point_unit = []
        point_unit = [item.__dict__ for item in config_point if item.id_type == 3]

        point_list = []
        register_list = []
        if hasattr(device_group_query, "templates_library"):
            templates_library = device_group_query.templates_library
            if hasattr(templates_library, "point_list"):
                # point_list =[item.__dict__ for item in templates_library.point_list]
                point_list = templates_library.point_list
                print(point_list[0].config)
            if hasattr(templates_library, "register_list"):
                register_list = templates_library.register_list

        return {
            "device_group": device_group_query,
            "data_type": data_type,
            "byte_order": byte_order,
            "point_unit": point_unit,
            "point_list": point_list,
            "register_list": register_list,
        }
    except Exception as err:
        print("Error : ", err)
        # LOGGER.error(f'--- {err} ---')
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# endregion

# region Point


# Describe functions before writing code
# 	 * @description get each point
# 	 * @author vnguyen
# 	 * @since 18-12-2023
# 	 * @param {info_point,db}
# 	 * @return data (PointTemplateOutBase)
@router.post("/point/get/", response_model=template_schemas.PointTemplateOutBase)
def get_each_point(
    info_point: template_schemas.PointInfoTemplateBase,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:
        point_query = db.query(models.Point_list).filter(
            models.Point_list.id == info_point.id_point
        )

        result_point = point_query.first()
        if not result_point:
            return formatMessage(
                f"Point with id: {info_point.id_point} does not exist",
                status.HTTP_404_NOT_FOUND,
            )

        config_point = (
            db.query(models.Config_information)
            .filter(models.Config_information.status == 1)
            .all()
        )
        data_type = []
        data_type = [item.__dict__ for item in config_point if item.id_type == 1]
        byte_order = []
        byte_order = [item.__dict__ for item in config_point if item.id_type == 2]
        point_unit = []
        point_unit = [item.__dict__ for item in config_point if item.id_type == 3]

        type_point = []
        type_point = [
            item.__dict__
            for item in config_point
            if item.id_type == 15 and item.type == 1
        ]
        type_class = []
        type_class = [
            item.__dict__
            for item in config_point
            if item.id_type == 15 and item.type == 2
        ]

        # result_point["type_units_list"]=point_unit

        return template_schemas.PointTemplateOutBase(
            **result_point.__dict__,
            type_units_list=point_unit,
            type_datatype_list=data_type,
            type_byteorder_list=byte_order,
            type_point_list=type_point,
            type_class_list=type_class,
        )
    except Exception as err:
        print("Error : ", err)
        # LOGGER.error(f'--- {err} ---')
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def refresh_table_device(
    id_template: int,
    last_index: int,
    new_points: list[template_schemas.PointOutBase],
    last_point: template_schemas.PointOutBase,
    db: Session,
):
    mppt_query = (
        db.query(models.Point_list)
        .filter(models.Point_list.id_template == id_template)
        .filter(models.Point_list.id_config_information > 266)
    )
    result_mppt = mppt_query.order_by(models.Point_list.index.asc()).all()
    for item in result_mppt:
        mppt_query.filter(models.Point_list.id == item.id).update(
            {"index": last_index}, synchronize_session=False
        )
        last_index += 1

    db.flush()

    used_template_devices = (
        db.query(deviceList_models.Device_list).filter(
            deviceList_models.Device_list.id_template == id_template
        )
    ).all()

    if used_template_devices:
        for item in used_template_devices:
            device_point_list_map_query = db.query(models.Device_point_list_map).filter(
                models.Device_point_list_map.id_device_list == item.id
            )

            device_point_list_map_query.delete(synchronize_session=False)
            db.flush()
            points_query = (
                db.query(models.Point_list)
                .filter(models.Point_list.id_template == id_template)
                .order_by(models.Point_list.index.asc())
            )
            points = points_query.all()
            for point in points:
                db.add(
                    models.Device_point_list_map(
                        id_device_list=item.id, id_point_list=point.id, name=point.name
                    )
                )

            db.flush()

            # db.execute(text("DROP TABLE IF EXISTS " + item.table_name))
            db.execute(text("DROP VIEW IF EXISTS " + item.view_table))

            column_to_add = [f"{item.id_pointkey} DOUBLE" for item in new_points]
            column_to_add = ", ".join(column_to_add)
            last_column = f" AFTER {last_point.id_pointkey}" if last_point else ""
            db.execute(
                text(
                    "ALTER TABLE "
                    + item.table_name
                    + " ADD COLUMN "
                    + column_to_add
                    + last_column
                    + ";"
                )
            )
            db.flush()
            table_name = f"dev_{str(item.id)}"
            # query_add_table_device = deviceList_models.create_table_device(
            #     table_name,
            #     [{"name": item.id_pointkey} for item in points]
            #     + [{"name": item.id_pointkey} for item in mppt_list_query],
            # )
            # print(f"query_add_table_device: {query_add_table_device}")
            # db.execute(CreateTable(query_add_table_device))
            # add view table of device
            tg = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
            view_table = f"dev_{str(item.id)}_{tg}"

            query_add_view_table_device = text(
                f"CREATE VIEW {view_table}  AS SELECT * from {table_name}"
            )
            print(f"query_add_view_table_device: {query_add_view_table_device}")
            db.execute(query_add_view_table_device)
            device_query = db.query(deviceList_models.Device_list).filter_by(id=item.id)
            device_query.update(
                {
                    "table_name": f"dev_{str(item.id)}",
                    "view_table": view_table,
                }
            )
            db.flush()
            # restart_pm2_change_template(id_template, db)


@router.post("/point/edit/all/", response_model=list[template_schemas.PointOutBase])
def update_point_list(
    id_template: int = Body(embed=True),
    points: list[template_schemas.PointOutBase] = Body(embed=True),
    db: Session = Depends(get_db),
):
    try:
        delete_point_list = (
            db.query(models.Point_list)
            .filter(models.Point_list.id_template == id_template)
            .filter(models.Point_list.id_config_information == 266)
        )

        delete_point_list.delete(synchronize_session=False)
        db.flush()

        for item in points:
            item.id_pointkey = item.name.replace(" ", "")
            item.id_template = id_template
            update_point = dict(
                **item.model_dump(
                    exclude=[
                        "type_units",
                        "type_datatype",
                        "type_byteorder",
                        "type_point_list",
                        "type_point",
                        "type_class",
                        "type_control",
                    ]
                ),
            )
            db.add(models.Point_list(**update_point))
        db.flush()

        last_index = points[-1].index + 1 if len(points) > 0 else 0
        refresh_table_device(id_template, last_index, points, db)
        db.commit()
        # region future update
        # mode_modbus_equation = (
        #     db.query(models.Config_information)
        #     .filter(models.Config_information.id == item.type_point.namekey)
        #     .first()
        # )
        # if not hasattr(mode_modbus_equation, "value"):
        #     return formatMessage(
        #         f"Equation with id: {item.type_point.namekey} does not exist",
        #         status.HTTP_404_NOT_FOUND,
        #     )
        # equation = mode_modbus_equation.value
        # print(f"equation: {equation}")
        # update_point = dict()
        # match equation:
        #     # Mode Modbus register
        #     case 1:
        #         update_point = dict(
        #             **item.model_dump(
        #                 exclude=[
        #                     "type_units",
        #                     "type_datatype",
        #                     "type_byteorder",
        #                     "type_point_list",
        #                     "type_point",
        #                     "type_class",
        #                 ]
        #             )
        #         )
        #     # Mode Equation
        #     case 2:
        #         update_point = dict(
        #             equation=item.constants,
        #             name=item.name,
        #             nameedit=item.nameedit,
        #             id_type_units=item.id_type_units,
        #             unitsedit=item.unitsedit,
        #         )
        #     case _:
        #         pass
        # endregion
        return points
    except exc.IntegrityError as err:
        print("=====================================")
        print("IntegrityError : ", err)
        print("=====================================")
        db.rollback()
        if "1048" in err.args[0]:
            return formatMessage(
                "Please fill in all required fields", status.HTTP_400_BAD_REQUEST
            )
        raise err
    except Exception as err:
        print("Error : ", err)
        db.rollback()
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Describe functions before writing code
# 	 * @description edit each point
# 	 * @author vnguyen
# 	 * @since 29-12-2023
# 	 * @param {info_point,db}
# 	 * @return data (PointOutBase)
@router.post("/point/edit/", response_model=schemas.PointOutBase)
def edit_each_point(
    point: schemas.PointOutBase,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:
        id_pointkey = point.name.replace(" ", "")

        last_index = point.index

        last_point = (
            db.query(models.Point_list)
            .filter(models.Point_list.id_template == point.id_template)
            .filter(models.Point_list.id_config_information == 266)
            .order_by(models.Point_list.index.desc())
            .first()
        )

        if point.id == None:
            point_query = (
                db.query(models.Point_list)
                .filter(models.Point_list.id_template == point.id_template)
                .filter(models.Point_list.id_pointkey == id_pointkey)
            )
            result_point = point_query.first()
            if result_point:
                return formatMessage(
                    f"Point with name: {point.name} already exists",
                    status.HTTP_406_NOT_ACCEPTABLE,
                )

            # region Add point if not exist
            add_point = models.Point_list(
                id_template=point.id_template,
                index=last_index,
                id_pointkey=id_pointkey,
                id_point_list_type=point.id_point_list_type,
                id_pointtype=point.id_pointtype,
                id_pointclass_type=point.id_pointclass_type,
                id_config_information=point.id_config_information,
                name=point.name,
                nameedit=point.nameedit,
                id_type_units=point.id_type_units,
                unitsedit=point.unitsedit,
                register=point.register,
                id_type_datatype=point.id_type_datatype,
                id_type_byteorder=point.id_type_byteorder,
                slope=point.slope,
                slopeenabled=point.slopeenabled,
                offset=point.offset,
                offsetenabled=point.offsetenabled,
                multreg=point.multreg,
                multregenabled=point.multregenabled,
                userscaleenabled=point.userscaleenabled,
                invalidvalue=point.invalidvalue,
                invalidvalueenabled=point.invalidvalueenabled,
                extendednumpoints=point.extendednumpoints,
                extendedregblocks=point.extendedregblocks,
                status=1,
                function=point.function,
                constants=point.constants,
            )

            db.add(add_point)
            db.flush()

            if last_point:
                last_index = (
                    last_point.index + 1
                    if last_point.index > last_index
                    else last_index + 1
                )
            db.refresh(add_point)
            refresh_table_device(
                point.id_template, last_index, [add_point], last_point, db
            )
            db.commit()
            # result_point = point_query.first()
            return add_point
        # endregion

        point_query = db.query(models.Point_list).filter(
            models.Point_list.id == point.id
        )

        update_point = dict(
            **point.model_dump(
                exclude=[
                    "type_units",
                    "type_datatype",
                    "type_byteorder",
                    "type_point_list",
                    "type_point",
                    "type_class",
                    "type_control",
                ]
            ),
        )
        point_query.update(update_point)
        db.flush()
        db.commit()
        # restart_pm2_change_template(point.id_template, db)
        # region future update
        # mode_modbus_equation = (
        #     db.query(models.Config_information)
        #     .filter(models.Config_information.id == info_point.equation)
        #     .first()
        # )
        # if not hasattr(mode_modbus_equation, "value"):
        #     return formatMessage(
        #         f"Equation with id: {info_point.equation} does not exist",
        #         status.HTTP_404_NOT_FOUND,
        #     )
        # equation = mode_modbus_equation.value
        # print(f"equation: {equation}")
        # id_template = info_point.id_template
        # update_point = dict()
        # match equation:
        #     # Mode Modbus register
        #     case 1:
        #         update_point = dict(**info_point.dict())
        #     # Mode Equation
        #     case 2:
        #         update_point = dict(
        #             equation=info_point.equation,
        #             name=info_point.name,
        #             nameedit=info_point.nameedit,
        #             id_type_units=info_point.id_type_units,
        #             unitsedit=info_point.unitsedit,
        #         )
        #     case _:
        #         pass
        # endregion
        return point
    except Exception as err:
        print("Error : ", err)
        # LOGGER.error(f'--- {err} ---')
        db.rollback()
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# # Describe functions before writing code
# # 	 * @description change number point
# # 	 * @author vnguyen
# # 	 * @since 08-01-2024
# # 	 * @param {PointChangeNumberBase,db}
# # 	 * @return data (PointBase)
# @router.post("/point/change_number/", response_model=list[schemas.PointBase])
# def change_number_point(
#     change_number_point: schemas.PointChangeNumberBase,
#     db: Session = Depends(get_db),
#     current_user: int = Depends(oauth2.get_current_user),
# ):
#     try:
#         number_point = change_number_point.number_point
#         id_template = change_number_point.id_template
#         point_query = (
#             db.query(models.Point_list)
#             .filter(models.Point_list.id_template == id_template)
#             .filter(models.Point_list.status == 1)
#         )
#         result_point = point_query.all()
#         if result_point and len(result_point) > 0:
#             count_point = len(result_point)
#             if number_point < count_point:
#                 print(f"----- Disable point -----")
#                 # delete
#                 array_delete = result_point[number_point:count_point]
#                 for item in array_delete:
#                     print(f"Disable Id: {item.id}")
#                     point_query.filter(models.Point_list.id == item.id).update(
#                         {"status": 0}
#                     )
#                 db.flush()
#                 restart_pm2_change_template(id_template, db)
#                 db.commit()
#                 point_query = db.query(models.Point_list).filter(
#                     models.Point_list.id_template == id_template
#                 )
#                 result_point = point_query.all()
#                 return result_point
#             elif number_point == count_point:
#                 print(f"----- Keep point -----")
#                 # no do
#                 point_query = db.query(models.Point_list).filter(
#                     models.Point_list.id_template == id_template
#                 )
#                 result_point = point_query.all()
#                 return result_point
#             else:
#                 print(f"----- Insert point -----")
#                 config_info_query = db.query(models.Config_information).filter(
#                     models.Config_information.status == 1
#                 )
#                 result_config_info = config_info_query.all()

#                 name = ""
#                 nameedit = False
#                 id_type_units = [
#                     item.__dict__
#                     for item in result_config_info
#                     if item.namekey == "(No units)" and item.id_type == 3
#                 ][0]["id"]
#                 unitsedit = False
#                 id_equation = [
#                     item.__dict__
#                     for item in result_config_info
#                     if item.namekey == "Modbus register" and item.id_type == 15
#                 ][0]["id"]
#                 id_config = [
#                     item.__dict__
#                     for item in result_config_info
#                     if item.namekey == "Input" and item.id_type == 15
#                 ][0]["id"]
#                 register = 0
#                 id_type_datatype = [
#                     item.__dict__
#                     for item in result_config_info
#                     if item.namekey == "Short" and item.id_type == 1
#                 ][0]["id"]
#                 id_type_byteorder = [
#                     item.__dict__
#                     for item in result_config_info
#                     if item.namekey == "normal" and item.id_type == 2
#                 ][0]["id"]
#                 slope = 1
#                 slopeenabled = False
#                 offset = 0
#                 offsetenabled = False
#                 multreg = 0
#                 multregenabled = False
#                 userscaleenabled = False
#                 invalidvalue = 65535
#                 invalidvalueenabled = False
#                 extendednumpoints = 0
#                 extendedregblocks = 0
#                 constants = 0
#                 function = ""
#                 # add
#                 number_point_add = number_point - count_point
#                 new_point_list = []

#                 for item in range(number_point_add):
#                     new_point = models.Point_list(
#                         id_template=id_template,
#                         name=name,
#                         nameedit=nameedit,
#                         id_type_units=id_type_units,
#                         unitsedit=unitsedit,
#                         equation=id_equation,
#                         config=id_config,
#                         register=register,
#                         id_type_datatype=id_type_datatype,
#                         id_type_byteorder=id_type_byteorder,
#                         slope=slope,
#                         slopeenabled=slopeenabled,
#                         offset=offset,
#                         offsetenabled=offsetenabled,
#                         multreg=multreg,
#                         multregenabled=multregenabled,
#                         userscaleenabled=userscaleenabled,
#                         invalidvalue=invalidvalue,
#                         invalidvalueenabled=invalidvalueenabled,
#                         extendednumpoints=extendednumpoints,
#                         extendedregblocks=extendedregblocks,
#                         status=1,
#                         function=function,
#                         constants=constants,
#                     )
#                     new_point_list.append(new_point)

#                 db.add_all(new_point_list)
#                 db.flush()
#                 device_point_list_query = db.query(models.Device_point_list).filter(
#                     models.Device_point_list.id_template == id_template
#                 )
#                 result_device_point_list = device_point_list_query.all()

#                 if result_device_point_list:
#                     # check number device
#                     device_list = list(
#                         set([item.id_device_list for item in result_device_point_list])
#                     )
#                     insert_device_point_list = []
#                     for item_point in new_point_list:
#                         for item_device in device_list:
#                             id_device_group = [
#                                 item.__dict__
#                                 for item in result_device_point_list
#                                 if item.id_device_list == item_device
#                             ][0]["id_device_group"]
#                             insert_device_point_list.append(
#                                 models.Device_point_list(
#                                     id_template=id_template,
#                                     id_device_group=id_device_group,
#                                     id_device_list=item_device,
#                                     id_point_list=item_point.id,
#                                 )
#                             )
#                     if insert_device_point_list:
#                         db.add_all(insert_device_point_list)
#                 # restart_pm2_change_template(id_template, db)
#                 db.commit()
#                 point_query = db.query(models.Point_list).filter(
#                     models.Point_list.id_template == id_template
#                 )
#                 result_point = point_query.all()
#                 # print(result_point)
#                 return result_point
#         else:
#             return formatMessage("Not have data", status.HTTP_404_NOT_FOUND)

#     except Exception as err:
#         print(f"Error: {err}")
#         # LOGGER.error(f'--- {err} ---')
#         return formatMessage(
#             "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
#         )


def refresh_when_delete(
    existed_point: list[dict], id_template: int, db: Session, type: int = 1
):  # 1: point, 2: mppt
    id_point_to_delte = [list(item.keys())[0] for item in existed_point]
    device_point_list_map_query = db.query(models.Device_point_list_map).filter(
        models.Device_point_list_map.id_point_list.in_(id_point_to_delte)
    )
    device_point_list_map_query.delete(synchronize_session=False)
    db.flush()

    used_template_devices = (
        db.query(deviceList_models.Device_list).filter(
            deviceList_models.Device_list.id_template == id_template
        )
    ).all()

    column_to_drop = [
        f"DROP COLUMN {list(item.values())[0].replace(' ', '')}"
        for item in existed_point
    ]
    column_to_drop = ", ".join(column_to_drop)

    devices_id = []
    if used_template_devices:
        for device in used_template_devices:
            devices_id.append(device.id)
            db.execute(text(f"ALTER TABLE {device.table_name} {column_to_drop};"))
        db.flush()

    if type == 2:
        for item in existed_point:
            if (
                item["id_config_information"] == 274
                or item["id_config_information"] == 275
            ):
                continue

            if item["id_config_information"] == 277:
                mppt_to_del = (
                    db.query(deviceList_models.Device_mppt)
                    .filter(
                        deviceList_models.Device_mppt.id_point_list
                        == list(item.keys())[0]
                    )
                    .filter(
                        deviceList_models.Device_mppt.id_device_list.in_(devices_id)
                    )
                )

                if mppt_to_del:
                    mppt_to_del.delete(synchronize_session=False)
                    db.flush()
                continue

            if item["id_config_information"] == 276:
                string_to_del = (
                    db.query(deviceList_models.Device_mppt_string)
                    .filter(
                        deviceList_models.Device_mppt_string.id_point_list
                        == list(item.keys())[0]
                    )
                    .filter(
                        deviceList_models.Device_mppt_string.id_device_list.in_(
                            devices_id
                        )
                    )
                )

                if string_to_del:
                    string_to_del.delete(synchronize_session=False)
                    db.flush()
                continue

            panel_to_del = (
                db.query(deviceList_models.Device_panel)
                .filter(
                    deviceList_models.Device_panel.id_point_list == list(item.keys())[0]
                )
                .filter(deviceList_models.Device_panel.id_device_list.in_(devices_id))
            )

            if panel_to_del:
                panel_to_del.delete(synchronize_session=False)
                db.flush()


# Describe functions before writing code
# 	 * @description delete point list
# 	 * @author vnguyen
# 	 * @since 08-01-2024
# 	 * @param {id,db}
# 	 * @return data (DeviceGroupOutBase)
@router.post(
    "/point/delete_multiple/", response_model=template_schemas.TemplateListBase
)
def delete_point_list(
    point_list: template_schemas.PointDeleteTemplateBase,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:
        id_template = point_list.id_template
        point_query = (
            db.query(models.Point_list)
            .filter(models.Point_list.id_template == id_template)
            .filter(models.Point_list.status == 1)
        )
        result_point = point_query.all()
        if not result_point:
            return formatMessage(
                f"Point with id: {id_template} does not exist",
                status.HTTP_404_NOT_FOUND,
            )

        existed_point = [
            {item.id_point: item.id_pointkey}
            for item in point_list.points
            if item.id_point in [item.id for item in result_point]
        ]

        for item in point_list.points:
            if existed_point.index({item.id_point: item.id_pointkey}) == -1:
                continue

            db.query(models.Point_list).filter(
                models.Point_list.id == item.id_point
            ).delete(synchronize_session=False)

        db.flush()

        refresh_when_delete(existed_point, id_template, db)
        db.commit()

        if len(existed_point) == 0:
            return formatMessage(
                "There are points that do not exist",
                status.HTTP_404_NOT_FOUND,
            )
        # restart_pm2_change_template(id_template, db)
        results = get_template_by_id(id_template, db)

        return results
    except Exception as err:
        print(f"Error: {err}")
        # LOGGER.error(f'--- {err} ---')
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Describe functions before writing code
# 	 * @description get MPPT, STRING, PANEL of Template
# 	 * @author vnguyen
# 	 * @since 16-01-2024
# 	 * @param {id,db}
# 	 * @return data (TemplateMPPTBase)
@router.post(
    "/mppt/get/template/",
    response_model=template_schemas.TemplateMPPTBase,
    response_model_by_alias=False,
)
def get_mppt_template(
    id_template: Optional[int] = Body(embed=True),
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:
        point_list_query = (
            db.query(models.Point_list)
            .filter(models.Point_list.id_template == id_template)
            .all()
        )
        if point_list_query:
            MPPT = [
                item for item in point_list_query if item.id_config_information == 277
            ]
            mppt = []
            if MPPT:
                for mppt_item in MPPT:
                    MPPT_STRING = [
                        item
                        for item in point_list_query
                        if item.parent == mppt_item.id
                        and item.id_config_information == 276
                    ]
                    String = []
                    if MPPT_STRING:
                        for string_item in MPPT_STRING:
                            MPPT_STRING_PANEL = [
                                item
                                for item in point_list_query
                                if item.parent == string_item.id
                                and item.id_config_information == 278
                            ]
                            Panel = []
                            if MPPT_STRING_PANEL:
                                Panel = [item.__dict__ for item in MPPT_STRING_PANEL]
                            String.append({**string_item.__dict__, "panel": Panel})

                    mppt.append({**mppt_item.__dict__, "string": String})

        return {"id": id_template, "mppt": mppt}
    except Exception as err:
        print("Error : ", err)
        # LOGGER.error(f'--- {err} ---')
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Describe functions before writing code
# 	 * @description create MPPT, STRING, PANEL of Template with 2 mode:
# 	 * @description 1. Create new MPPT, STRING, PANEL
# 	 * @description 2. Clone last MPPT, STRING, PANEL
# 	 * @author nhan.tran
# 	 * @since 09-04-2024
# 	 * @param {create_information,db}
# 	 * @return data (TemplateListBase)
@router.post(
    "/mppt/create/",
    response_model=template_schemas.TemplateListBase,
    response_model_by_alias=False,
)
def create_mppt(
    create_information: template_schemas.MPPTCreateBase, db: Session = Depends(get_db)
):
    id_template = create_information.id_template
    is_clone = create_information.is_clone_last_mppt
    num_of_mppt = create_information.num_of_mppt
    num_of_string = create_information.num_of_string
    num_of_panel = create_information.num_of_panel

    try:
        last_mppt = (
            db.query(models.Point_list)
            .filter(models.Point_list.id_template == id_template)
            .filter(models.Point_list.id_config_information == 277)
            .order_by(models.Point_list.index.desc())
            .first()
        )

        used_template_devices = (
            db.query(deviceList_models.Device_list).filter(
                deviceList_models.Device_list.id_template == id_template
            )
        ).all()

        last_point = (
            db.query(models.Point_list)
            .filter(models.Point_list.id_template == id_template)
            .order_by(models.Point_list.index.desc())
            .first()
        )
        last_index = last_point.index + 1 if last_point else 0

        if not last_mppt:
            last_mppt = models.Point_list(
                id_template=id_template,
                id_pointkey="MPPT0",
                id_config_information=277,
                name="MPPT0",
                index=last_index,
            )

        mppt_count = (
            db.query(models.Point_list)
            .filter(models.Point_list.id_template == id_template)
            .filter(models.Point_list.id_config_information == 277)
            .count()
        )

        mppt_children = (
            db.query(models.Point_list)
            .filter(models.Point_list.id_template == id_template)
            .filter(models.Point_list.id_config_information == 276)
            .filter(models.Point_list.parent == last_mppt.id)
            .all()
        )

        string_children = (
            db.query(models.Point_list)
            .filter(models.Point_list.id_template == id_template)
            .filter(models.Point_list.id_config_information == 278)
            .filter(models.Point_list.parent.in_([item.id for item in mppt_children]))
            .all()
        )

        mppt_count += 1

        new_mppt_point = template_schemas.PointBase(
            id_template=id_template,
            id_pointkey="MPPT0",
            id_config_information=277,
            name="MPPT0",
        )

        if is_clone:
            new_mppt_point = template_schemas.PointBase(**last_mppt.__dict__)

        for i in range(num_of_mppt):
            mppt_children = (
                db.query(models.Point_list)
                .filter(models.Point_list.id_template == id_template)
                .filter(models.Point_list.parent == new_mppt_point.id)
                .all()
            )

            string_children = (
                db.query(models.Point_list)
                .filter(models.Point_list.id_template == id_template)
                .filter(models.Point_list.id_config_information == 278)
                .filter(
                    models.Point_list.parent.in_([item.id for item in mppt_children])
                )
                .all()
            )

            if new_mppt_point.id_pointkey == f"MPPT{mppt_count}":
                mppt_count += 1

            new_mppt_point.index = last_index
            new_mppt_point.id_pointkey = f"MPPT{mppt_count}"
            new_mppt_point.name = f"MPPT{mppt_count}"
            new_mppt = models.Point_list(**new_mppt_point.model_dump(exclude=["id"]))

            db.add(new_mppt)
            db.flush()
            last_index += 1

            if len(mppt_children) < 2 or not is_clone:
                new_mppt_voltage = template_schemas.PointBase(
                    id_template=id_template,
                    id_pointkey=f"{new_mppt.id_pointkey}Voltage",
                    id_config_information=274,
                    name=f"{new_mppt.name} Voltage",
                    parent=new_mppt.id,
                )
                new_mppt_current = template_schemas.PointBase(
                    id_template=id_template,
                    id_pointkey=f"{new_mppt.id_pointkey}Current",
                    id_config_information=275,
                    name=f"{new_mppt.name} Current",
                    parent=new_mppt.id,
                )

                mppt_children = [new_mppt_voltage, new_mppt_current]

            if not is_clone:
                new_string = template_schemas.PointBase(
                    id_template=id_template,
                    id_config_information=276,
                )
                mppt_children += [new_string for _ in range(num_of_string)]
            string_count = 0
            new_mppt_children = []
            new_string_children = {}

            for string in mppt_children:
                new_string = template_schemas.PointBase(**string.__dict__)
                new_string.index = last_index
                new_string.parent = new_mppt.id

                if (
                    new_string.id_config_information == 274
                    or new_string.id_config_information == 275
                ):
                    new_string.id_pointkey = f"{new_mppt.id_pointkey}{'Voltage' if new_string.id_config_information == 274 else 'Current'}"
                    new_string.name = f"{new_mppt.name} {'Voltage' if new_string.id_config_information == 274 else 'Current'}"
                    new_string = models.Point_list(
                        **new_string.model_dump(exclude=["id"])
                    )
                    db.add(new_string)
                    db.flush()
                    last_index += 1
                    new_mppt_children.append(new_string)
                    continue

                new_string.id_pointkey = (
                    f"{new_mppt.id_pointkey}String{string_count + 1}"
                )
                new_string.name = f"String {string_count + 1}"
                new_string = models.Point_list(**new_string.model_dump(exclude=["id"]))
                string_count += 1
                db.add(new_string)
                db.flush()
                new_mppt_children.append(new_string)

                if not is_clone:
                    new_panel = template_schemas.PointBase(
                        id_template=id_template,
                        id_config_information=278,
                    )

                    string_children = [new_panel for _ in range(num_of_panel)]

                last_index += 1
                panel_count = 0
                new_string_children[new_string.id] = []
                for panel in string_children:
                    if panel.id_config_information == 278 and panel.parent == string.id:
                        new_panel = template_schemas.PointBase(**panel.__dict__)

                        new_panel.index = last_index
                        new_panel.id_pointkey = (
                            f"{new_string.id_pointkey}Panel{panel_count + 1}"
                        )
                        new_panel.name = f"Panel {panel_count + 1}"
                        new_panel.parent = new_string.id

                        new_panel_to_add = models.Point_list(
                            **new_panel.model_dump(exclude=["id"])
                        )
                        panel_count += 1
                        db.add(new_panel_to_add)
                        db.flush()
                        new_string_children[new_string.id].append(new_panel_to_add)
                        last_index += 1

            if used_template_devices:
                for device in used_template_devices:
                    table_name = device.table_name
                    column_to_add = []
                    device_mppt = deviceList_models.Device_mppt(
                        id_point_list=new_mppt.id,
                        id_device_list=device.id,
                        name=new_mppt.name,
                        namekey=new_mppt.id_pointkey,
                    )
                    db.add(device_mppt)

                    db.add(
                        models.Device_point_list_map(
                            id_device_list=device.id,
                            id_point_list=new_mppt.id,
                            name=new_mppt.name,
                        )
                    )

                    column_to_add.append(f"ADD COLUMN {new_mppt.id_pointkey} DOUBLE")

                    db.flush()

                    for string in new_mppt_children:
                        column_to_add.append(f"ADD COLUMN {string.id_pointkey} DOUBLE")
                        db.add(
                            models.Device_point_list_map(
                                id_device_list=device.id,
                                id_point_list=string.id,
                                name=string.name,
                            )
                        )
                        if string.id_config_information == 276:
                            string_mppt = deviceList_models.Device_mppt_string(
                                id_device_mppt=device_mppt.id,
                                id_point_list=string.id,
                                id_device_list=device.id,
                                name=string.name,
                                namekey=string.id_pointkey,
                            )
                            db.add(string_mppt)

                            db.flush()

                            for panel in new_string_children[string.id]:
                                column_to_add.append(
                                    f"ADD COLUMN {panel.id_pointkey} DOUBLE"
                                )
                                db.add(
                                    models.Device_point_list_map(
                                        id_device_list=device.id,
                                        id_point_list=panel.id,
                                        name=panel.name,
                                    )
                                )
                                if (
                                    panel.id_config_information == 278
                                    and panel.parent == string.id
                                ):
                                    db.add(
                                        deviceList_models.Device_panel(
                                            id_device_string=string_mppt.id,
                                            id_point_list=panel.id,
                                            id_device_list=device.id,
                                            name=panel.name,
                                        )
                                    )

                                    db.flush()
                    db.execute(
                        text(f"ALTER TABLE {table_name} {', '.join(column_to_add)};")
                    )
                db.flush()

            mppt_count += 1
        db.commit()

        return get_template_by_id(id_template, db)
    except Exception as err:
        print("Error : ", err)
        db.rollback()
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Describe functions before writing code
# 	 * @description delete mppt point list
# 	 * @author vnguyen
# 	 * @since 08-01-2024
# 	 * @param {id,db}
# 	 * @return data (DeviceGroupOutBase)
@router.post("/mppt/delete_multiple/", response_model=template_schemas.TemplateListBase)
def delete_mppt_point_list(
    point_list: template_schemas.MPPTPointDeleteTemplateBase,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:
        id_template = point_list.id_template
        point_query = (
            db.query(models.Point_list)
            .filter(models.Point_list.id_template == id_template)
            .filter(models.Point_list.id_config_information > 266)
            .filter(models.Point_list.status == 1)
        )
        result_point = point_query.all()
        if not result_point:
            return formatMessage(
                f"Point with id: {id_template} does not exist",
                status.HTTP_404_NOT_FOUND,
            )

        existed_point = [
            {
                item.id_point: item.id_pointkey,
                "id_config_information": item.id_config_information,
            }
            for item in point_list.points
            if item.id_point in [item.id for item in result_point]
        ]

        for item in point_list.points:
            if item.id_config_information == 274 or item.id_config_information == 275:
                if item.parent not in [item.id_point for item in point_list.points]:
                    return formatMessage(
                        f"Bad request: Must delete MPPT and its children together",
                        status.HTTP_406_NOT_ACCEPTABLE,
                    )

        missing_children = []
        for item in point_list.points:
            if item.parent == None:
                continue

            children = (
                db.query(models.Point_list)
                .filter(models.Point_list.parent == item.id_point)
                .all()
            )
            for child in children:
                if child.id not in [item.id_point for item in point_list.points]:
                    missing_children.append(child.name)

        if missing_children:
            return formatMessage(
                f"{', '.join(missing_children)} {'does' if len(missing_children) == 1 else 'do'} not exist",
                status.HTTP_404_NOT_FOUND,
            )

        for item in point_list.points:
            db.query(models.Point_list).filter(
                models.Point_list.id == item.id_point
            ).delete(synchronize_session=False)

        db.flush()
        refresh_when_delete(existed_point, id_template, db, type=2)

        # restart_pm2_change_template(id_template, db)
        db.commit()

        if len(existed_point) == 0:
            return formatMessage(
                "Bad request: Must delete MPPT and its children together",
                status.HTTP_404_NOT_FOUND,
            )

        results = get_template_by_id(id_template, db)
        return results
    except Exception as err:
        print(f"Error: {err}")
        # LOGGER.error(f'--- {err} ---')
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def update_register_list(
    id_template: int, registers: list[schemas.RegisterOutBase], db: Session
):
    if registers:
        for item in registers:
            register_query = (
                db.query(models.Register_block)
                .filter(models.Register_block.id_template == id_template)
                .filter(models.Register_block.id == item.id)
            )
            result_register = register_query.first()
            if not result_register:
                return formatMessage(
                    f"Register with id: {item.id} does not exist",
                    status.HTTP_404_NOT_FOUND,
                )
            register_query.update(dict(**item.model_dump(exclude=["type_function"])))
        db.flush()
        return registers
    return None


def update_mppt(list_mppt: list[models.ManualPointList], id_template: int, db: Session):
    existed_mppt = (
        db.query(models.Point_list)
        .filter(models.Point_list.id_template == id_template)
        .filter(models.Point_list.id_config_information > 266)
        .all()
    )

    existed_mppt_id = [item.id for item in existed_mppt]

    db.flush()


# endregion


# region Register
# Describe functions before writing code
# 	 * @description get register list
# 	 * @author vnguyen
# 	 * @since 10-01-2024
# 	 * @param {db}
# 	 * @return data (RegisterConfigOutBase)
@router.post("/register/get/", response_model=schemas.RegisterConfigOutBase)
def get_register_list(
    id_template: Optional[int] = Body(embed=True),
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:
        register_query = db.query(models.Register_block).filter(
            models.Register_block.id_template == id_template
        )
        result_register = register_query.all()
        if not result_register:
            return formatMessage(
                f"Register with id: {id_template} does not exist",
                status.HTTP_404_NOT_FOUND,
            )

        config_register = (
            db.query(models.Config_information)
            .filter(models.Config_information.status == 1)
            .all()
        )
        type_function = []
        type_function = [item.__dict__ for item in config_register if item.id_type == 5]
        return {"register_list": result_register, "type_function": type_function}
    except Exception as err:
        print("Error : ", err)
        # LOGGER.error(f'--- {err} ---')
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Describe functions before writing code
# 	 * @description edit each register
# 	 * @author vnguyen
# 	 * @since 10-01-2024
# 	 * @param {info_register,db}
# 	 * @return data (RegisterOutBase)
@router.post("/register/edit/", response_model=schemas.RegisterOutBase)
def edit_each_register(
    info_register: schemas.RegisterOutBase,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:
        id = info_register.id
        id_template = info_register.id_template
        register_query = db.query(models.Register_block).filter(
            models.Register_block.id == id
        )
        result_register = register_query.first()
        print(result_register.__dict__)
        if not result_register:
            return formatMessage(
                f"Register with id: {id} does not exist", status.HTTP_404_NOT_FOUND
            )
        # restart_pm2_change_template(id_template, db)
        register_query.update(info_register.dict())
        db.commit()
        return result_register
    except Exception as err:
        print("Error : ", err)
        # LOGGER.error(f'--- {err} ---')
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Describe functions before writing code
# 	 * @description edit all register
# 	 * @author vnguyen
# 	 * @since 10-01-2024
# 	 * @param {register_list,db}
# 	 * @return data (RegisterOutBase)
@router.post("/register/edit_multiple/", response_model=list[schemas.RegisterOutBase])
def edit_all_register(
    register_list: list[schemas.RegisterOutBase],
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:
        id_template = register_list[0].id_template

        register_query = db.query(models.Register_block).filter(
            models.Register_block.id_template == id_template
        )
        for item in register_list:
            register_query.filter(models.Register_block.id == item.id).update(
                item.dict()
            )
        db.commit()
        # restart_pm2_change_template(id_template, db)
        return register_query

    except Exception as err:
        print(f"Error: {err}")
        # LOGGER.error(f'--- {err} ---')
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Describe functions before writing code
# 	 * @description delete register
# 	 * @author vnguyen
# 	 * @since 10-01-2024
# 	 * @param {id,db}
# 	 * @return data (RegisterOutBase)
@router.post("/register/delete/", response_model=list[schemas.RegisterOutBase])
def delete_register(
    register_list: list[schemas.RegisterOutBase],
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:
        id_template = register_list[0].id_template
        register_query = db.query(models.Register_block).filter(
            models.Register_block.id_template == id_template
        )
        result_register = register_query.all()
        if not result_register:
            return formatMessage(
                f"Register with id: {id_template} does not exist",
                status.HTTP_404_NOT_FOUND,
            )

        for item in register_list:
            register_query.filter(models.Register_block.id == item.id).delete(
                synchronize_session=False
            )

        # restart_pm2_change_template(id_template, db)
        db.commit()
        return register_query.all()
    except Exception as err:
        print(f"Error: {err}")
        # LOGGER.error(f'--- {err} ---')
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# endregion


# region Export
# Describe functions before writing code
# 	 * @description export template file
# 	 * @author vnguyen
# 	 * @since 16-01-2024
# 	 * @param {id,db}
# 	 * @return data (RegisterOutBase)
@router.post("/export_file/", response_model=list[schemas.RegisterOutBase])
def export_file(
    id_template: Optional[int] = Body(embed=True),
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:

        template_query = db.query(models.Register_block).filter(
            models.Register_block.id_template == id_template
        )
        result_template = template_query.all()
        if not result_template:
            return formatMessage(
                f"Template with id: {id_template} does not exist",
                status.HTTP_404_NOT_FOUND,
            )

        # db.commit()
        # return register_query.all()
    except Exception as err:
        print(f"Error: {err}")
        # LOGGER.error(f'--- {err} ---')
        return formatMessage(
            "Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/charting/")
async def charting(
    db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)
):
    try:
        param = {
            "table_device_list": "device_list",
            "status": 1,
            "groupInverter": [
                "dev_00002",
                "dev_00003",
                "dev_00004",
                "dev_00005",
                "dev_00006",
                "dev_00296",
                "dev_00303",
                "dev_00304",
                "dev_00305",
                "dev_00306",
                "dev_00307",
            ],
        }
        # query_sql=""
        # result=db.execute(query_sql)
        # db.commit()
        # print(result)
        # query_sql= cov_xml_sql("selectDevice",param)
        query_sql = cov_xml_sql("EnergyMapper.xml", "getDataIrradianceToday", param)

        # print(f'query_sql: {query_sql}')

        result = db.execute(text(str(query_sql))).all()

        results_dict = [row._asdict() for row in result]
        print(f"results_dict: {len(results_dict)}")
        # print(result)
        # template_query = db.query(models.datalog_inv1)
        # result_template=template_query.all()
        # print(result_template[0].__dict__)

        return {"message": "successfully added vote"}
    except Exception as err:
        print(f"Error: {err}")
        # LOGGER.error(f'--- {err} ---')


# endregion
