# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import datetime
import ipaddress
import json
import os
import signal
import subprocess
import sys
from pprint import pprint
from typing import Annotated, Optional, Union

import mybatis_mapper2sql
# import oauth2
# import schemas
from async_timeout import timeout
from fastapi import (APIRouter, Body, Depends, FastAPI, HTTPException, Query,
                     Response, status)
from fastapi.responses import JSONResponse
from flask import jsonify
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import exc, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, insert, join, literal_column, text

from utils.response_msg_helper import formatMessage

path = (
    lambda project_name: (
        os.path.dirname(__file__)[
            : len(project_name) + os.path.dirname(__file__).find(project_name)
        ]
        if project_name and project_name in os.path.dirname(__file__)
        else -1
    )
)("src")
sys.path.append(path)

# from contextlib import asynccontextmanager

from sqlalchemy import (BigInteger, Column, DateTime, Float, ForeignKey,
                        Integer, MetaData, String, Table, create_engine)
# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.schema import CreateTable, DropTable

import api.domain.deviceGroup.models as deviceGroup_models
import api.domain.deviceList.models as deviceList_models
import api.domain.deviceList.schemas as deviceList_schemas
import api.domain.template.models as template_models
import model.models as models
import utils.oauth2 as oauth2
from database.db import Base, engine, get_db
from utils.libCom import cov_xml_sql, get_mybatis
from utils.mqttManager import mqtt_public
# from model import schemas
# from utils import (create_device_group_rs485_run_pm2, create_program_pm2,
#                    delete_program_pm2, find_program_pm2, get_mybatis, path,
#                    restart_pm2_change_template, restart_program_pm2,
#                    restart_program_pm2_many)
from utils.pm2Manager import (create_device_group_rs485_run_pm2,
                              create_program_pm2, delete_program_pm2,
                              find_program_pm2, restart_pm2_change_template,
                              restart_program_pm2, restart_program_pm2_many)

# path=path_directory_relative("ipc_api") # name of project
# sys.path.append(path)
router = APIRouter(prefix="/device_list", tags=["DeviceList"])

# /device_list/
# /device_list
import warnings

warnings.filterwarnings(
    "ignore", ".*Class SelectOfScalar will not make use of SQL compilation caching.*"
)
from sqlalchemy import exc as sa_exc

# with warnings.catch_warnings():
#     warnings.simplefilter("ignore", category=sa_exc.SAWarning)

# Describe functions before writing code
# /**
# 	 * @description get only device
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,db}
# 	 * @return data (DeviceListOut)
# 	 */


@router.post("/", response_model=deviceList_schemas.DeviceListOfPointListOut)
def get_only_device(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # print(f'id: {id}')

    # ----------------------
    Device_list = (
        db.query(deviceList_models.Device_list)
        .filter(deviceList_models.Device_list.id == id)
        .first()
    )
    # Device_list=Device_list.__dict__
    # print(f'device_list :{Device_list}')
    # ----------------------
    # result = db.execute(
    # text(f'select * from user')).all()
    # results_dict = [row._asdict() for row in result]
    # print(f'{results_dict}')
    # ----------------------
    if not Device_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} does not exist",
        )

    return Device_list


# Describe functions before writing code
# /**
# 	 * @description get all device
# 	 * @author vnguyen
# 	 * @since 04-12-2023
# 	 * @param {idb}
# 	 * @return data (DeviceListOut)
# 	 */


@router.post("/all/", response_model=list[deviceList_schemas.DeviceListShortOut])
def get_all_device(
    db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)
):
    # print(f'id: {id}')
    # ----------------------
    Device_list = db.query(deviceList_models.Device_list)
    # Device_list=Device_list.__dict__
    # ----------------------
    if not Device_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Device empty"
        )
    # print(Device_list.all()[0].device_type.__dict__)
    # print(Device_list.all()[0].communication.driver_list.__dict__)
    result_device_list = Device_list.all()
    deviceLists = []
    for item in result_device_list:
        # Port=""
        # if item.communication.driver_list.name=='Modbus/TCP':
        #     Port=f'{item.tcp_gateway_ip}:{item.tcp_gateway_port}@{item.rtu_bus_address}'
        # elif  item.communication.driver_list.name== "RS485":
        #     Port=f'{item.communication.name}@{ str(item.rtu_bus_address).zfill(4)}'
        # else:
        #     pass
        deviceLists.append(
            {
                "id": item.id,
                "name": item.name,
                "rtu_bus_address": item.rtu_bus_address,
                "tcp_gateway_ip": item.tcp_gateway_ip,
                "tcp_gateway_port": item.tcp_gateway_port,
                "status": item.status,
                "device_type_name": item.device_type.name,
                "driver_type": item.communication.driver_list.name,
            }
        )

    return deviceLists


# Describe functions before writing code
# /**
# 	 * @description get device config
# 	 * @author vnguyen
# 	 * @since 01-12-2023
# 	 * @param {db}
# 	 * @return data (DeviceConfigOut)
# 	 */


@router.post("/config/", response_model=deviceList_schemas.DeviceConfigOut)
def get_device_config(
    db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)
):
    # print(f'id: {id}')
    # ----------------------
    device_type_query = db.query(models.Device_type)
    if not device_type_query.all():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Device type does not exist"
        )
    device_group_query = db.query(deviceGroup_models.Device_group)
    if not device_group_query.all():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Device group does not exist"
        )
    # device_list_query = db.query(deviceList_models.Device_list).order_by(deviceList_models.Device_list.id.asc())
    template_query = db.query(template_models.Template_library).order_by(
        template_models.Template_library.id.asc()
    )

    communication_query = db.query(models.Communication)

    result_device_type = []
    for item in device_type_query.all():
        result_device_type.append(item.__dict__)
    result_device_group = []
    for item in device_group_query.all():
        new_item = item.__dict__
        # new_item["templates_library"]=item.templates_library.__dict__
        result_device_group.append(new_item)
    # result_device_list=[]
    # for item in device_list_query.all():
    #     result_device_list.append(item.__dict__)
    result_communication = []
    for item in communication_query.all():
        new_item = item.__dict__
        new_item["driver_list"] = item.driver_list.__dict__
        result_communication.append(new_item)
    result_template = []
    for item in template_query.all():
        # new_item=item.__dict__
        template_item = {
            **item.__dict__,
        }
        id_template = item.id
        result_template.append(template_item)

    return {
        # "device_list":result_device_list,
        "device_type": result_device_type,
        "device_group": result_device_group,
        "communication": result_communication,
        "template": result_template,
    }


# Describe functions before writing code
# /**
# 	 * @description create multiple device
# 	 * @author vnguyen
# 	 * @since 11-12-2023
# 	 * @param {DeviceCreate,db}
# 	 * @return data (DeviceState)
# 	 */


@router.post("/create_multiple/", response_model=deviceList_schemas.DeviceState)
async def create_multiple_device(
    create_device: deviceList_schemas.MultipleDeviceCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:

        def reset_data_new(new_device_list):
            # {
            # "name": "ABB-2",
            # "device_virtual": false,
            # "id_communication": 3,
            # "rtu_bus_address":1,
            # "tcp_gateway_port": 502,
            # "tcp_gateway_ip": "192.168.80.101",
            # "id_device_type": 1,
            # "add_count": 2,
            # "in_mode": 1,
            # "id_template": 3
            # }
            # {
            # "name": "MFM383A",
            # "device_virtual": false,
            # "id_communication": 1,
            # "rtu_bus_address":1,
            # "tcp_gateway_port": 502,
            # "tcp_gateway_ip": "",
            # "id_device_type": 6,
            # "add_count": 1,
            # "in_mode": 0,
            # "id_template": 6
            # }
            # delete device in table device_list
            for items in new_device_list:
                db.query(deviceList_models.Device_list).filter_by(id=items.id).delete()
                db.commit()
                print(f"Delete device: {items.id}")
            # delete all table created
            for i, items in enumerate(new_device_list):
                # name_device=f'dev_{str(items.id).zfill(5)}'
                tg = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
                view_table = f"dev_{str(items.id)}_{tg}"
                db.execute(text(f"DROP VIEW IF EXISTS {view_table}"))
                name_device = f"dev_{str(items.id)}"
                db.execute(text(f"DROP TABLE {name_device}"))
            return 300

        def filter_group_mppt_string_panel():
            pass

        async def execute_func():
            try:
                print("------------")
                id_communication = create_device.id_communication
                id_template = create_device.id_template
                communication_query = (
                    db.query(models.Communication)
                    .filter(models.Communication.id == id_communication)
                    .first()
                )

                # mppt=create_device.mppt.mppt_number
                # print(f'mppt: {mppt}')

                point_list_query = (
                    db.query(models.Point_list)
                    .filter(models.Point_list.id_template == id_template)
                    .all()
                )
                try:
                    if communication_query:
                        pass
                    if communication_query.driver_list:
                        pass
                except Exception as err:
                    print(err)
                    return 300
                finally:
                    pass
                driver_list = communication_query.driver_list
                # insert new device to table
                new_device_list = []
                add_count = create_device.add_count  # == 0 mode add only one
                in_mode = create_device.in_mode

                # ----------------------------------------
                for item in range(add_count):
                        rated_power=None
                        if create_device.rated_power!= None:
                            rated_power=(create_device.rated_power)
                        rated_power_custom=  rated_power
                        min_watt_in_percent=5               
                        pv=16
                        model=0
                        send_p=0
                        send_q=0
                        send_pf=0
                        value_pf=1       
                        # max=100
                        enable_poweroff=0
                        mode=0
                        # tcp_gateway_ip=create_device.tcp_gateway_ip
                        name=create_device.name
                        device_virtual=create_device.device_virtual
                        id_communication=create_device.id_communication
                        rtu_bus_address=create_device.rtu_bus_address
                        tcp_gateway_port=create_device.tcp_gateway_port
                        tcp_gateway_ip=create_device.tcp_gateway_ip
                        id_device_type=create_device.id_device_type
                        id_project_setup=1
                        # id_device_group=create_device.id_device_group
                        
                        # network address
                        if in_mode==1:                          
                            ip = create_device.tcp_gateway_ip.split(".")
                            host_id=int(ip[3])+item
                            if  host_id>=255 :
                                host_id=254
                            tcp_gateway_ip=f'{ip[0]}.{ip[1]}.{ip[2]}.{host_id}'
                        # bus-address
                        elif in_mode==2:
                            rtu_bus_address=int(create_device.rtu_bus_address) + item
                        elif in_mode==0:
                            pass
                        else:
                            return 300 
                        if driver_list.name=="RS485":
                            tcp_gateway_ip=None
                            tcp_gateway_port=None
                        # elif driver_list.name=="Modbus/TCP":
                        #     pass
                        # else:
                        #     pass
                        new_device = deviceList_models.Device_list(
                                                        id_project_setup=id_project_setup,
                                                        table_name="",
                                                        view_table="",
                                                        pv=pv,
                                                        model=model,
                                                        mode=mode,
                                                        send_p=send_p,
                                                        send_q=send_q,
                                                        send_pf=send_pf,
                                                        value_pf=value_pf,
                                                        # max=max,
                                                        enable_poweroff=enable_poweroff,
                                                        name=name,
                                                        device_virtual=device_virtual,
                                                        id_communication=id_communication,
                                                        rtu_bus_address=rtu_bus_address,
                                                        tcp_gateway_port=tcp_gateway_port,
                                                        tcp_gateway_ip=tcp_gateway_ip,
                                                        id_device_type=id_device_type,
                                                        id_template=id_template,
                                                        # id_device_group=id_device_group                                                                                                                                                                                                                                                               # **create_device.dict()
                                                        rated_power=rated_power,
                                                        rated_power_custom= rated_power_custom,
                                                        min_watt_in_percent=min_watt_in_percent 
                                                        )
                        new_device_list.append(new_device)
                db.add_all(new_device_list)
                db.flush()
                # Get all point
                point_list_query = (
                    db.query(models.Point_list)
                    .filter_by(id_template=id_template)
                    .order_by(models.Point_list.index.asc())
                    .all()
                )

                point_list_name = []
                for item in point_list_query:
                    point_list_name.append({
                        "id":item.id,
                        "name":item.id_pointkey})
                
                # Update status table `device_point_list_map`
                
                ## add mppt, string, panel 
                if create_device.mppt:
                    for i,items in enumerate(new_device_list): 
                        id_device_list=items.id
                        for i,mppt_item in enumerate(create_device.mppt):
                            
                            
                            mppt_object=[item for item in point_list_query if item.id == mppt_item.id][0]
                            id_point_list=mppt_object.id
                            print(f'id_point_list: {id_point_list}')
                            new_mppt = deviceList_models.Device_mppt(
                                                                    id_device_list=id_device_list,
                                                                    id_point_list=id_point_list,
                                                                    name=mppt_object.name,
                                                                    status= mppt_item.status,
                                                                    namekey=mppt_item.id_pointkey
                                                                )
                            db.add(new_mppt)
                            db.flush()
                            print(f'MPPT ---------------------')
                            for i,string_item in enumerate(mppt_item.string):
                                string_name=[item for item in point_list_query if item.id == string_item.id][0].name
                                panel_number=len(string_item.panel)
                                id_point_list=string_item["id"]
                                new_string = deviceList_models.Device_mppt_string(
                                                                        id_device_mppt=new_mppt.id,
                                                                        id_device_list=id_device_list,
                                                                        id_point_list=id_point_list,
                                                                        name=string_name, 
                                                                        status= string_item.status,
                                                                        namekey=string_item.id_pointkey,
                                                                        panel=panel_number
                                                                )
                                db.add(new_string)
                                db.flush()
                                print(f'STRING ---------------------')
                                for i,panel_item in enumerate(string_item.panel):
                                    print(f'PANEL ---------------------')
                                    panel_name=[item for item in point_list_query if item.id == panel_item.id][0].name
                                    id_point_list=panel_item["id"]
                                    new_panel = deviceList_models.Device_panel(
                                                                        id_device_list=id_device_list,
                                                                        id_point_list=id_point_list,
                                                                        id_device_string=new_string.id,
                                                                        status= panel_item.status,
                                                                        name=panel_name
                                                                )
                                    db.add(new_panel)
                                    db.flush()   

                # add table of device
                for idd, item in enumerate(new_device_list):
                    try:
                        # add table of device
                        table_name = f"dev_{str(item.id)}"
                        query_add_table_device = deviceList_models.create_table_device(
                            table_name, point_list_name
                        )
                        print(f"query_add_table_device: {query_add_table_device}")
                        db.execute(CreateTable(query_add_table_device))
                        # add view table of device
                        tg = datetime.datetime.now(datetime.timezone.utc).strftime(
                            "%Y%m%d"
                        )
                        view_table = f"dev_{str(item.id)}_{tg}"
                        # createview = deviceList_models.CreateView(f'dev_{str(item.id)}_{tg}',select(query_add_table_device))
                        # query_add_view_table_device=text(str(createview))
                        query_add_view_table_device = text(
                            f"CREATE VIEW {view_table}  AS SELECT * from {table_name}"
                        )
                        print(
                            f"query_add_view_table_device: {query_add_view_table_device}"
                        )
                        db.execute(query_add_view_table_device)
                        device_query = db.query(
                            deviceList_models.Device_list
                        ).filter_by(id=item.id)
                        device_query.update(
                            {
                                "table_name": f"dev_{str(item.id)}",
                                "view_table": view_table,
                            }
                        )
                        db.flush()

                    except exc.SQLAlchemyError as err:
                        # delete device in table device_list
                        print(f"Error: {err.args[0]}")
                        db.rollback()
                        for items in new_device_list:
                            db.query(deviceList_models.Device_list).filter_by(
                                id=items.id
                            ).delete()
                            db.commit()
                            print(f"Delete device: {items.id}")
                        # delete all table created
                        for i, items in enumerate(new_device_list):
                            # if i<idd:
                            name_device = f"dev_{str(items.id)}"
                            print(f"Delete table device: {name_device}")
                            db.execute(text(f"DROP TABLE IF EXISTS {name_device}"))

                            tg = datetime.datetime.now(datetime.timezone.utc).strftime(
                                "%Y%m%d"
                            )
                            view_table = f"dev_{str(items.id)}_{tg}"
                            print(f"Delete view table device: {view_table}")
                            db.execute(text(f"DROP VIEW IF EXISTS {view_table}"))
                        return 300
                    finally:
                        pass
                db.commit()
                if driver_list.name == "RS485":
                    try:
                        # rowcount_register_block=0
                        rowcount_point_list = 0
                        # insert device_point_list
                        new_device = []
                        for item in new_device_list:
                            # param={
                            #     "id":item.id
                            # }
                            # sql_query_insert_device_point_list= cov_xml_sql("deviceConfig.xml","insert_device_point_list",param)
                            sql_query_insert_device_point_list = f"INSERT INTO `device_point_list_map`( \
                            id_device_list,\
                            id_point_list,\
                            name,\
                            low_alarm,\
                            high_alarm\
                            )\
                            SELECT \
                            device_list.id,\
                            point_list.id AS id_point_list,\
                            point_list.name AS name,\
                            point_list.low_alarm AS low_alarm,\
                            point_list.high_alarm AS high_alarm\
                            FROM device_list \
                            INNER JOIN template_library ON template_library.id=device_list.id_template \
                            INNER JOIN point_list ON template_library.id=point_list.id_template \
                            WHERE device_list.id= {item.id}  ORDER BY point_list.id ASC;"
                            result_point_list = db.execute(
                                text(sql_query_insert_device_point_list)
                            )
                            print(f"result_point_list: {result_point_list.__dict__}")
                            if result_point_list.rowcount != 0:
                                rowcount_point_list += 1
                            new_device.append({
                                "id":item.id,
                                "name":item.name,
                                "connect_type":driver_list.name,
                                "id_com":id_communication,
                                "mode":item.mode
                                })
                        if rowcount_point_list == 0:
                            reset_data_new(new_device_list)
                        db.commit()
                        point_list_mppt_update = []
                        if create_device.mppt:
                            for i, items in enumerate(new_device_list):
                                id_device_list = items.id
                                for i, mppt_item in enumerate(create_device.mppt):
                                    mppt_object = [
                                        item
                                        for item in point_list_query
                                        if item.id == mppt_item.id
                                    ][0]
                                    id_parent = mppt_object.id
                                    if id_parent:
                                        result = (
                                            db.query(
                                                models.Device_point_list_map.id,
                                                models.Device_point_list_map.id_device_list,
                                                models.Device_point_list_map.name,
                                                models.Config_information.namekey,
                                                models.Device_point_list_map.status,
                                            )
                                            .select_from(models.Device_point_list_map)
                                            .join(
                                                models.Point_list,
                                                models.Point_list.id
                                                == models.Device_point_list_map.id_point_list,
                                            )
                                            .join(
                                                models.Config_information,
                                                models.Config_information.id
                                                == models.Point_list.id_config_information,
                                            )
                                            .filter(
                                                models.Device_point_list_map.id_device_list
                                                == id_device_list
                                            )
                                            .filter(
                                                models.Point_list.parent == id_parent
                                            )
                                            .filter(
                                                models.Config_information.namekey.like(
                                                    "MPPT%"
                                                )
                                            )
                                            .all()
                                        )

                                        point_list_mppt = [
                                            dict(
                                                id=item[0],
                                                id_device_list=item[1],
                                                name=item[2],
                                                namekey=item[3],
                                                status=mppt_item.status,
                                            )
                                            for item in result
                                        ]
                                        # print(point_list_mppt)
                                        for item in point_list_mppt:
                                            point_list_mppt_update.append(item)

                                        for i, string_item in enumerate(
                                            mppt_item.string
                                        ):
                                            string_object = [
                                                item
                                                for item in point_list_query
                                                if item.id == string_item.id
                                            ][0]
                                            id_parent = mppt_object.id
                                            panel_number = len(string_item.panel)
                                            result = (
                                                db.query(
                                                    models.Device_point_list_map.id,
                                                    models.Device_point_list_map.id_device_list,
                                                    models.Device_point_list_map.name,
                                                    models.Config_information.namekey,
                                                    models.Device_point_list_map.status,
                                                )
                                                .select_from(
                                                    models.Device_point_list_map
                                                )
                                                .join(
                                                    models.Point_list,
                                                    models.Point_list.id
                                                    == models.Device_point_list_map.id_point_list,
                                                )
                                                .join(
                                                    models.Config_information,
                                                    models.Config_information.id
                                                    == models.Point_list.id_config_information,
                                                )
                                                .filter(
                                                    models.Device_point_list_map.id_device_list
                                                    == id_device_list
                                                )
                                                .filter(
                                                    models.Point_list.parent
                                                    == id_parent
                                                )
                                                .filter(
                                                    models.Config_information.namekey.like(
                                                        "StringAmps%"
                                                    )
                                                )
                                                .all()
                                            )

                                            point_list_mppt = [
                                                dict(
                                                    id=item[0],
                                                    id_device_list=item[1],
                                                    name=item[2],
                                                    namekey=item[3],
                                                    status=string_item.status,
                                                )
                                                for item in result
                                            ]
                                            for item in point_list_mppt:
                                                point_list_mppt_update.append(item)
                                            for i, panel_item in enumerate(
                                                string_item.panel
                                            ):
                                                id_parent = string_item.id
                                                # print(f'id_parent: {id_parent}')
                                                result = (
                                                    db.query(
                                                        models.Device_point_list_map.id,
                                                        models.Device_point_list_map.id_device_list,
                                                        models.Device_point_list_map.name,
                                                        models.Config_information.namekey,
                                                        models.Device_point_list_map.status,
                                                    )
                                                    .select_from(
                                                        models.Device_point_list_map
                                                    )
                                                    .join(
                                                        models.Point_list,
                                                        models.Point_list.id
                                                        == models.Device_point_list_map.id_point_list,
                                                    )
                                                    .join(
                                                        models.Config_information,
                                                        models.Config_information.id
                                                        == models.Point_list.id_config_information,
                                                    )
                                                    .filter(
                                                        models.Device_point_list_map.id_device_list
                                                        == id_device_list
                                                    )
                                                    .filter(
                                                        models.Point_list.parent
                                                        == id_parent
                                                    )
                                                    .filter(
                                                        models.Point_list.id
                                                        == panel_item.id
                                                    )
                                                    .filter(
                                                        models.Config_information.namekey.like(
                                                            "Panel%"
                                                        )
                                                    )
                                                    .all()
                                                )

                                                point_list_mppt = [
                                                    dict(
                                                        id=item[0],
                                                        id_device_list=item[1],
                                                        name=item[2],
                                                        namekey=item[3],
                                                        status=panel_item.status,
                                                    )
                                                    for item in result
                                                ]
                                                for item in point_list_mppt:
                                                    point_list_mppt_update.append(item)

                        for item in point_list_mppt_update:
                            result = (
                                db.query(models.Device_point_list_map)
                                .filter(
                                    models.Device_point_list_map.id_device_list
                                    == int(item["id_device_list"])
                                )
                                .filter(
                                    models.Device_point_list_map.id == int(item["id"])
                                )
                                .update({"status": item["status"]})
                            )
                            db.commit()
                        #
                        param = {
                            "CODE": "CreateRS485Dev", 
                            "PAYLOAD": {
                                "id_communication":id_communication,
                                "device":new_device
                            }
                            }
                        mqtt_public("/Init/API/Requests", param)
                        return 100
                    except exc.SQLAlchemyError as err:
                        # delete device in table device_list
                        print(err.args[0])
                        db.rollback()
                        reset_data_new(new_device_list)
                    finally:
                        pass
                elif driver_list.name == "Modbus/TCP":
                    rowcount_point_list = 0
                    new_device = []
                    try:
                        # insert device_point_list
                        for item in new_device_list:
                            # sql_query_insert_device_point_list= cov_xml_sql("deviceConfig.xml",
                            #                                                 "insert_device_point_list",{"id":item.id})
                            sql_query_insert_device_point_list = f"INSERT INTO `device_point_list_map`( \
                            id_device_list,\
                            id_point_list,\
                            name,\
                            low_alarm,\
                            high_alarm\
                            )\
                            SELECT \
                            device_list.id,\
                            point_list.id AS id_point_list,\
                            point_list.name AS name,\
                            point_list.low_alarm AS low_alarm,\
                            point_list.high_alarm AS high_alarm\
                            FROM device_list \
                            INNER JOIN template_library ON template_library.id=device_list.id_template \
                            INNER JOIN point_list ON template_library.id=point_list.id_template \
                            WHERE device_list.id= {item.id}  ORDER BY point_list.id ASC;"
                            result_point_list = db.execute(
                                text(sql_query_insert_device_point_list)
                            )
                            print(f"result_point_list: {result_point_list.__dict__}")
                            if result_point_list.rowcount != 0:
                                rowcount_point_list +=1
                            new_device.append({
                                "id":item.id,
                                "name":item.name,
                                "connect_type":driver_list.name,
                                "id_communication":id_communication,
                                "mode":item.mode
                                })
                        db.commit()
                        point_list_mppt_update = []
                        if create_device.mppt:
                            for i, items in enumerate(new_device_list):
                                id_device_list = items.id
                                for i, mppt_item in enumerate(create_device.mppt):
                                    mppt_object = [
                                        item
                                        for item in point_list_query
                                        if item.id == mppt_item.id
                                    ][0]
                                    id_parent = mppt_object.id
                                    if id_parent:
                                        result = (
                                            db.query(
                                                models.Device_point_list_map.id,
                                                models.Device_point_list_map.id_device_list,
                                                models.Device_point_list_map.name,
                                                models.Config_information.namekey,
                                                models.Device_point_list_map.status,
                                            )
                                            .select_from(models.Device_point_list_map)
                                            .join(
                                                models.Point_list,
                                                models.Point_list.id
                                                == models.Device_point_list_map.id_point_list,
                                            )
                                            .join(
                                                models.Config_information,
                                                models.Config_information.id
                                                == models.Point_list.id_config_information,
                                            )
                                            .filter(
                                                models.Device_point_list_map.id_device_list
                                                == id_device_list
                                            )
                                            .filter(
                                                models.Point_list.parent == id_parent
                                            )
                                            .filter(
                                                models.Config_information.namekey.like(
                                                    "MPPT%"
                                                )
                                            )
                                            .all()
                                        )

                                        point_list_mppt = [
                                            dict(
                                                id=item[0],
                                                id_device_list=item[1],
                                                name=item[2],
                                                namekey=item[3],
                                                status=mppt_item.status,
                                            )
                                            for item in result
                                        ]
                                        # print(point_list_mppt)
                                        for item in point_list_mppt:
                                            point_list_mppt_update.append(item)

                                        for i, string_item in enumerate(
                                            mppt_item.string
                                        ):
                                            string_object = [
                                                item
                                                for item in point_list_query
                                                if item.id == string_item.id
                                            ][0]
                                            id_parent = mppt_object.id
                                            panel_number = len(string_item.panel)
                                            result = (
                                                db.query(
                                                    models.Device_point_list_map.id,
                                                    models.Device_point_list_map.id_device_list,
                                                    models.Device_point_list_map.name,
                                                    models.Config_information.namekey,
                                                    models.Device_point_list_map.status,
                                                )
                                                .select_from(
                                                    models.Device_point_list_map
                                                )
                                                .join(
                                                    models.Point_list,
                                                    models.Point_list.id
                                                    == models.Device_point_list_map.id_point_list,
                                                )
                                                .join(
                                                    models.Config_information,
                                                    models.Config_information.id
                                                    == models.Point_list.id_config_information,
                                                )
                                                .filter(
                                                    models.Device_point_list_map.id_device_list
                                                    == id_device_list
                                                )
                                                .filter(
                                                    models.Point_list.parent
                                                    == id_parent
                                                )
                                                .filter(
                                                    models.Config_information.namekey.like(
                                                        "StringAmps%"
                                                    )
                                                )
                                                .all()
                                            )

                                            point_list_mppt = [
                                                dict(
                                                    id=item[0],
                                                    id_device_list=item[1],
                                                    name=item[2],
                                                    namekey=item[3],
                                                    status=string_item.status,
                                                )
                                                for item in result
                                            ]
                                            for item in point_list_mppt:
                                                point_list_mppt_update.append(item)
                                            for i, panel_item in enumerate(
                                                string_item.panel
                                            ):
                                                id_parent = string_item.id
                                                # print(f'id_parent: {id_parent}')
                                                result = (
                                                    db.query(
                                                        models.Device_point_list_map.id,
                                                        models.Device_point_list_map.id_device_list,
                                                        models.Device_point_list_map.name,
                                                        models.Config_information.namekey,
                                                        models.Device_point_list_map.status,
                                                    )
                                                    .select_from(
                                                        models.Device_point_list_map
                                                    )
                                                    .join(
                                                        models.Point_list,
                                                        models.Point_list.id
                                                        == models.Device_point_list_map.id_point_list,
                                                    )
                                                    .join(
                                                        models.Config_information,
                                                        models.Config_information.id
                                                        == models.Point_list.id_config_information,
                                                    )
                                                    .filter(
                                                        models.Device_point_list_map.id_device_list
                                                        == id_device_list
                                                    )
                                                    .filter(
                                                        models.Point_list.parent
                                                        == id_parent
                                                    )
                                                    .filter(
                                                        models.Point_list.id
                                                        == panel_item.id
                                                    )
                                                    .filter(
                                                        models.Config_information.namekey.like(
                                                            "Panel%"
                                                        )
                                                    )
                                                    .all()
                                                )

                                                point_list_mppt = [
                                                    dict(
                                                        id=item[0],
                                                        id_device_list=item[1],
                                                        name=item[2],
                                                        namekey=item[3],
                                                        status=panel_item.status,
                                                    )
                                                    for item in result
                                                ]
                                                for item in point_list_mppt:
                                                    point_list_mppt_update.append(item)

                        for item in point_list_mppt_update:
                            result = (
                                db.query(models.Device_point_list_map)
                                .filter(
                                    models.Device_point_list_map.id_device_list
                                    == int(item["id_device_list"])
                                )
                                .filter(
                                    models.Device_point_list_map.id == int(item["id"])
                                )
                                .update({"status": item["status"]})
                            )

                        db.commit()
                        #
                        #
                        if rowcount_point_list == 0:
                            reset_data_new(new_device_list)
                            return 300
                        else:
                            db.close()
                    except exc.SQLAlchemyError as err:
                        # delete device in table device_list
                        print(err.args[0])
                        db.rollback()
                        reset_data_new(new_device_list)
                    finally:
                        if rowcount_point_list != 0:
                            param = {
                                    "CODE": "CreateTCPDev", 
                                    "PAYLOAD": new_device}
                            mqtt_public("/Init/API/Requests", param)
                        return 100
                else:
                    return 300
                return 100
            except Exception as err:
                print("Error create table : ", err)
                return 300

        async with timeout(15) as cm:
            response = await execute_func()
            if response == 100:  # ok
                return formatMessage(str(response), status.HTTP_200_OK)
            elif response == 200:  # alarm
                return {"status": "alert", "code": str(response)}
            elif response == 300:  # error
                return formatMessage(str(response), status.HTTP_400_BAD_REQUEST)
            else:
                return formatMessage(
                    str(response), status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    except asyncio.TimeoutError:
        return formatMessage("Server is busy", status.HTTP_408_REQUEST_TIMEOUT)


# Describe functions before writing code
# /**
# 	 * @description get point list
# 	 * @author vnguyen
# 	 * @since 04-12-2023
# 	 * @param {id,db}
# 	 * @return data (DevicePointListBase)
# 	 */
@router.post(
    "/point_list/", response_model=list[deviceList_schemas.DevicePointListBase]
)
def get_point_list_only_device(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    # ----------------------
    device_point_list_query = (
        db.query(models.Device_point_list)
        .filter(models.Device_point_list.id_device_list == id)
        .all()
    )
    #
    if not device_point_list_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id: {id} does not exist",
        )

    # return {"point_list":device_point_list_query}
    return device_point_list_query


# Describe functions before writing code
# /**
# 	 * @description delete device
# 	 * @author vnguyen
# 	 * @since 04-12-2023
# 	 * @param {id,db}
# 	 * @return data (DeviceState)
# 	 */
@router.post("/delete/", response_model=deviceList_schemas.DeviceState)
async def delete_device(
    delete_device: deviceList_schemas.DeviceDeleteMulti,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:

        if not delete_device.mode in [1, 2]:
            return JSONResponse(
                content={"detail": "Mode does not exist"}, status_code=404
            )
        device_list = delete_device.device
        mode = delete_device.mode
        delete_list = []
        try:
            for i, item in enumerate(device_list):
                result_device = db.query(deviceList_models.Device_list).filter_by(
                    id=item.id
                )
                if result_device.first():
                    device = result_device.first()
                    view_table = device.view_table
                    table_name = device.table_name
                    id_communication = device.id_communication
                    #
                    driver_list = ""
                    if hasattr(device.communication, "driver_list"):
                        if hasattr(device.communication.driver_list, "name"):
                            driver_list = device.communication.driver_list.name

                    delete_list.append(
                        {
                            "mode": mode,
                            "id": item.id,
                            "name": device.name,
                            "id_communication": id_communication,
                            "driver_name": driver_list,
                        }
                    )
                    if mode == 1:  # Disable
                        result_device.update({"status": 0})
                        # status =0 of device in table device_list
                        # Disable pm2 send list to api gateway
                        # Delete pm2 app device running
                        # Restart pm2: LogDevice, LogFile, UpData
                    elif mode == 2:  # delete
                        # Delete table and view of device
                        db.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                        db.execute(text(f"DROP VIEW IF EXISTS {view_table}"))
                        result_device.delete()
                        # Delete device in table device_list
                        # Delete pm2 send list to api gateway
                        # Delete pm2 app device running
                        # Restart pm2: LogDevice, LogFile, UpData
                    else:
                        pass
            db.commit()
            print(f"delete_list: {delete_list}")
        except exc.SQLAlchemyError as err:
            db.rollback()
            print("Error delete the device : ", err)
            return JSONResponse(
                content={"detail": "HTTP_404_NOT_FOUND"}, status_code=404
            )
        finally:
            if delete_list:
                param={
                    "CODE":"DeleteDev",
                    "PAYLOAD":delete_list,
                    "DELETE_MODE":mode
                }
                mqtt_public("/Init/API/Requests",param)
            return {"status": "success","code": str(100)}
    except Exception as err:
        raise HTTPException(status_code=500, detail="Internal server error")


# Describe functions before writing code
# /**
# 	 * @description update device
# 	 * @author vnguyen
# 	 * @since 13-12-2023
# 	 * @param {DeviceUpdateBase,db}
# 	 * @return data (DeviceState)
# 	 */
@router.post("/update/", response_model=deviceList_schemas.DeviceState)
async def update_device_basic(
    update_device: deviceList_schemas.DeviceUpdateBase,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:
        # need restart pm2
        # name --> allow change
        # id_project_setup --> allow change
        # device_virtual --> lock
        # id_device_type --> lock
        # id_communication --> lock
        # id_device_group if change it
        # - delete all in table device_point_list
        # - delete all in table device_register_block
        # - init parameter in table device_point_list
        # - init parameter in table device_register_block
        # rtu_bus_address --> allow change
        # tcp_gateway_ip --> allow change
        # tcp_gateway_port --> allow change

        # chon group khac
        # delete all device_point_list
        # edit point/register block
        # template_library
        # delete all device_point_list
        # --> init app in pm2
        def init_pm2_dev_tcp(id, name, id_communication, connect_type):
            # Find app pm2
            result_find_app_pm2 = find_program_pm2(
                f"Dev|{str(id_communication)}|{connect_type}|{id}|"
            )
            if result_find_app_pm2 == 100:
                # delete success app pm2
                result_delete_app_pm2 = delete_program_pm2(
                    f"Dev|{str(id_communication)}|{connect_type}|{id}|"
                )
                if result_delete_app_pm2 != 100:
                    return 200
                else:
                    # init start pm2 app
                    pid = f"Dev|{id_communication}|{connect_type}|{id}|{name}"
                    create_program_pm2(f"{path}/deviceDriver/ModbusTCP.py", pid, id)
                    return 100
            else:
                # init start pm2 app
                pid = f"Dev|{id_communication}|{connect_type}|{id}|{name}"
                create_program_pm2(f"{path}/deviceDriver/ModbusTCP.py", pid, id)
                return 100

        def init_pm2_dev_rs485(id_communication, sql_select_device):
            result_find_app_pm2 = find_program_pm2(f"Dev|{str(id_communication)}|")
            if result_find_app_pm2 == 100:
                result_delete_app_pm2 = delete_program_pm2(
                    f"Dev|{str(id_communication)}|"
                )
                if result_delete_app_pm2 != 100:
                    return 300
                # check list device and Exclusions device new
                device_list_query = (
                    db.query(deviceList_models.Device_list)
                    .filter(
                        deviceList_models.Device_list.id_communication
                        == id_communication
                    )
                    .filter(deviceList_models.Device_list.status == 1)
                    .order_by(deviceList_models.Device_list.id.asc())
                    .all()
                )
                # check device same group rs485 com port
                item_rs485 = [
                    item.__dict__
                    for item in device_list_query
                    if item.id_communication == id_communication
                ]
                # # find device in group rs485
                # if not item_rs485:
                #     reset_data_new(new_device_list)
                if item_rs485:
                    # check group rs485 same com port
                    result_device_group_rs485 = db.execute(
                        text(sql_select_device),
                        params={"id_communication": id_communication},
                    ).all()
                    results_device_group_dict = [
                        row._asdict() for row in result_device_group_rs485
                    ]
                    # if not results_device_group_dict:
                    #     reset_data_new(new_device_list)
                    # init restart pm2 app same rs485
                    create_device_group_rs485_run_pm2(path, results_device_group_dict)
                    # restart pm2 app log
                    restart_program_pm2(f"Log")
                    return 100
            elif result_find_app_pm2 != 100:
                print(
                    "---------- create group RS485 same com port when list device empty ----------"
                )
                # check group rs485 same com port
                result_device_group_rs485 = db.execute(
                    text(sql_select_device),
                    params={"id_communication": id_communication},
                ).all()
                results_device_group_dict = [
                    row._asdict() for row in result_device_group_rs485
                ]
                # if not results_device_group_dict:
                #     reset_data_new(new_device_list)
                # init restart pm2 app same rs485
                create_device_group_rs485_run_pm2(path, results_device_group_dict)
                # restart pm2 app log
                restart_program_pm2(f"Log")
                return 100
            else:
                return 300

        async def execute_func():
            try:
                id = update_device.id
                name = update_device.name
                id_communication = update_device.id_communication
                rtu_bus_address = update_device.rtu_bus_address
                tcp_gateway_port = update_device.tcp_gateway_port
                tcp_gateway_ip = update_device.tcp_gateway_ip
                id_device_type = update_device.id_device_type
                id_template = update_device.id_template
                mode_update = update_device.mode_update
                # id_communication
                device_list_query = db.query(deviceList_models.Device_list).filter_by(
                    id=id
                )
                result_device_list = device_list_query.first()

                if not result_device_list:
                    return JSONResponse(
                        content={"detail": f"Device with id: {id} does not exist"},
                        status_code=status.HTTP_404_NOT_FOUND,
                    )
                #  Check template have change
                # --> Not have data
                # mode_update=2 # data delete
                # Delete table
                # Delete data in table `device_point_list_map`
                # Delete data in table `sync_data`
                # --> Have data
                # mode_update=1 # data keep
                # mode_update=2 # data delete
                # Delete table
                # Delete data in table `device_point_list_map`
                # Delete data in table `sync_data`
                # --> Update id_communication
                # check id_com old
                # --> TCP
                # Delete pm2 Dev
                # Create pm2 Dev
                # --> RS485
                # Delete group RS485
                # Create new group RS485

                # --> Update rtu_bus_address,tcp_gateway_port,tcp_gateway_ip, name
                # Delete pm2 Dev --> create pm2 Dev
                # restart pm2 LogDevice
                # restart pm2 UpData
                # restart pm2 LogFile
                # Step 1: Delete pm2 Dev
                # Step 2: Check and delete data
                # Step 3: Update new data to table
                # Step 4: Create pm2 new Dev
                # Step 5: restart pm2 need to use
                id_communication_old = result_device_list.id_communication
                name_old = update_device.name
                id_communication_old = result_device_list.id_communication
                rtu_bus_address_old = result_device_list.rtu_bus_address
                tcp_gateway_port_old = result_device_list.tcp_gateway_port
                tcp_gateway_ip_old = result_device_list.tcp_gateway_ip
                id_device_type_old = result_device_list.id_device_type
                id_template_old = result_device_list.id_template
                connect_type_old = result_device_list.communication.driver_list.name
                # Step 1 --------------------------------------------------------------
                if connect_type_old == "Modbus/TCP":
                    await delete_program_pm2(
                        f"Dev|{str(id_communication_old)}|{connect_type_old}|{id}|"
                    )
                elif connect_type_old == "RS485":
                    await delete_program_pm2(f"Dev|{str(id_communication_old)}|")
                else:
                    return 300
                # Step 2 --------------------------------------------------------------
                if mode_update == 1:  # data keep
                    pass
                elif mode_update == 2:  # data delete
                    # Delete data in table `device_list`
                    db.query(deviceList_models.Device_list).filter_by(id=id).delete()
                    # Delete table
                    db.execute(text(f"DROP TABLE dev_{id}"))
                    # Delete data in table `device_point_list_map`
                    db.query(models.Device_point_list_map).filter_by(
                        id_device_list=id
                    ).delete()

                    # Delete data in table `sync_data`
                    db.query(models.Sync_data).filter_by(id_device_list=id).delete()
                    db.commit()
                else:
                    pass
                #
                # result_mybatis=get_mybatis(path+'/mybatis/device.xml')
                # sql_register_block=result_mybatis["insert_device_register_block"]
                # sql_point_list=result_mybatis["insert_device_point_list"]
                # sql_select_device=result_mybatis["select_all_device"]
                # check changed id_device_group, If it changed Re-initialize --> device_point_list and device_register_block
                result_check_id_device_group = (
                    db.query(deviceList_models.Device_list)
                    .filter(deviceList_models.Device_list.id == id)
                    .filter(
                        deviceList_models.Device_list.id_device_group == id_device_group
                    )
                    .first()
                )
                if not result_check_id_device_group:  # Re-initialize
                    try:
                        print(
                            f"Re-initialize --> id: {id}| id_device_group: {id_device_group}|"
                        )
                        result_del_device_point_list = (
                            db.query(models.Device_point_list)
                            .filter_by(id_device_list=id)
                            .delete()
                        )
                        result_del_device_register_block = (
                            db.query(models.Device_register_block)
                            .filter_by(id_device_list=id)
                            .delete()
                        )
                        db.flush()
                        update_data = update_device.dict()
                        device_list_query.filter(
                            deviceList_models.Device_list.id == id
                        ).update(update_data, synchronize_session=False)
                        result_register_block = db.execute(
                            text(sql_register_block), params={"id": id}
                        )
                        result_point_list = db.execute(
                            text(sql_point_list), params={"id": id}
                        )
                        db.flush()
                        if (
                            result_del_device_point_list
                            and result_del_device_register_block
                            and result_register_block.rowcount > 0
                            and result_point_list.rowcount > 0
                        ):
                            print(f"Delete all point and register block of Device")
                            db.commit()
                            # app pm2
                            if connect_type == "Modbus/TCP":
                                init_pm2_dev_tcp(
                                    id, name, id_communication, connect_type
                                )
                                restart_program_pm2(f"Log")
                            elif connect_type == "RS485":
                                init_pm2_dev_rs485(id_communication, sql_select_device)
                            else:
                                return 300

                    except Exception as err:
                        print(err)
                        db.rollback()

                else:  # keep
                    print(f"Update --> id: {id}| id_device_group: {id_device_group}|")
                    update_data = update_device.dict()
                    device_list_query.filter(
                        deviceList_models.Device_list.id == id
                    ).update(update_data, synchronize_session=False)
                    db.commit()
                    if connect_type == "Modbus/TCP":
                        init_pm2_dev_tcp(id, name, id_communication, connect_type)
                        restart_program_pm2(f"Log")
                    elif connect_type == "RS485":
                        init_pm2_dev_rs485(id_communication, sql_select_device)
                    else:
                        return 300

            except Exception as err:
                print("Error update device : ", err)
                return 300

        async with timeout(5) as cm:
            response = await execute_func()
            if response == 100:  # ok
                return {"status": "success", "code": str(response)}
            elif response == 200:  # alarm
                return {"status": "alert", "code": str(response)}
            elif response == 300:  # error
                return {"status": "error", "code": str(response)}
            else:
                return {"status": "error", "code": "400"}

    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timeout")


# Describe functions before writing code
# /**
# 	 * @description check device have data
# 	 * @author vnguyen
# 	 * @since 15-03-2024
# 	 * @param {DeviceUpdateBase,db}
# 	 * @return data (DeviceState)
# 	 */
@router.post("/exists_data/", response_model=deviceList_schemas.DeviceExistDataOut)
async def check_device_data(
    update_device: deviceList_schemas.DeviceUpdateBase,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    try:
        id = update_device.id
        device_list_query = db.query(deviceList_models.Device_list).filter_by(id=id)
        result_device_list = device_list_query.first()
        if not result_device_list:
            return JSONResponse(
                content={"detail": f"Device with id: {id} does not exist"},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        # check device have data
        have_table_query = f"SELECT * FROM dev_{id}"
        result = db.execute(text(have_table_query)).first()
        if result == None:
            return {"status": "Device not exists data", "code": str(100)}
        else:
            return {"status": "Device exists data", "code": str(302)}
    except Exception as err:
        raise HTTPException(status_code=500, detail="Internal server error")
