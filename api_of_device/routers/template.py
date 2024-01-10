# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import datetime
import ipaddress
import json
from pprint import pprint
from typing import Annotated, Optional, Union

import models
import mybatis_mapper2sql
import oauth2
import schemas
import utils
from async_timeout import timeout
from database import get_db
from fastapi import (APIRouter, Body, Depends, FastAPI, HTTPException, Query,
                     Response, status)
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import exc
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, insert, join, literal_column, select, text
from utils import (create_device_group_rs485_run_pm2, create_program_pm2,
                   delete_program_pm2, find_program_pm2, get_mybatis, path,
                   restart_pm2_change_template, restart_program_pm2,
                   restart_program_pm2_many)

router = APIRouter(
    prefix="/template",
    tags=['Template']
)

# Describe functions before writing code
# /**
# 	 * @description create template
# 	 * @author vnguyen
# 	 * @since 10-01-2024
# 	 * @param {template,db}
# 	 * @return data (TemplateOutBase)
# 	 */
@router.post('/create/', response_model=schemas.TemplateOutBase)
def create_template(template: schemas.TemplateCreateBase,db: Session = Depends(get_db) ):
    try:
        name=template.name
        template_query = db.query(models.Template_library).filter(
        models.Template_library.name == name).first()
        if template_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Template name already exists")
        
        new_template = models.Template_library(**template.dict())
        db.add(new_template)
        db.commit()
        db.refresh(new_template)
        
        return new_template
    except (exc.SQLAlchemyError,Exception) as err:
        print('Error : ',err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not have data")
# Describe functions before writing code
# /**
# 	 * @description delete template
# 	 * @author vnguyen
# 	 * @since 10-01-2024
# 	 * @param {,db}
# 	 * @return data ()
# 	 */
# Describe functions before writing code
# /**
# 	 * @description edit template
# 	 * @author vnguyen
# 	 * @since 10-01-2024
# 	 * @param {,db}
# 	 * @return data ()
# 	 */
@router.post('/edit_each/', response_model=schemas.DeviceGroupOutBase)
def edit_each_template(template: schemas.TemplateUpdateBase,db: Session = Depends(get_db) ):
    try:
        id=template.id
        template_query = db.query(models.Template_library).filter(
        models.Template_library.id == id)
        result_template=template_query.first()
        if not result_template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Template with id: {id} does not exist")
        
        template_query.update(template.dict())
        restart_pm2_change_template(id,db)
        db.commit()
        return result_template
    except (exc.SQLAlchemyError,Exception) as err:
        print('Error : ',err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not have data")
# Describe functions before writing code
# /**
# 	 * @description get template list
# 	 * @author vnguyen
# 	 * @since 10-01-2024
# 	 * @param {db}
# 	 * @return data (TemplateBase)
# 	 */
@router.post('/get_all/', response_model=list[schemas.TemplateBase])
def get_list( db: Session = Depends(get_db) ):
    try:
        template_query = db.query(models.Template_library)
        result_template=template_query.all()
        if not result_template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Template list empty")

        return result_template
    except (exc.SQLAlchemyError,Exception) as err:
        print('Error : ',err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not have data")
# Describe functions before writing code
# /**
# 	 * @description get each template
# 	 * @author vnguyen
# 	 * @since 28-12-2023
# 	 * @param {id_template,db}
# 	 * @return data (TemplateListBase)
# 	 */
@router.post('/get_each_template/', response_model=schemas.TemplateListBase)
def get_each_template(id_template: Optional[int] = Body(embed=True), db: Session = Depends(get_db) ):
    try:
        template_query = db.query(models.Template_library).filter(
        models.Template_library.id == id_template).first()
        if not template_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Template with id: {id} does not exist")
        # print(device_group_query.__dict__)
        config_point = db.query(models.Config_information).filter(models.Config_information.status 
                                                                                == 1).all()
        data_type=[]
        data_type = [item.__dict__ for item in config_point if item.id_type == 1]
        byte_order=[]
        byte_order = [item.__dict__ for item in config_point if item.id_type == 2]
        point_unit=[]
        point_unit = [item.__dict__ for item in config_point if item.id_type == 3]
        
        register_list=[]
        point_list=[]
        register_query = db.query(models.Register_block).filter(
        models.Register_block.id_template == id_template)
        register_list=register_query.all()
        # 
        point_query = db.query(models.Point_list).filter(
        models.Point_list.id_template == id_template)
        point_list=point_query.all()
        
        return {
            "data_type":data_type,
            "byte_order":byte_order,
            "point_unit":point_unit,
            "point_list":point_list,
            "register_list":register_list
        }
    except (exc.SQLAlchemyError,Exception) as err:
        print('Error : ',err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not have data")
# Describe functions before writing code
# /**
# 	 * @description get template group device
# 	 * @author vnguyen
# 	 * @since 28-12-2023
# 	 * @param {id_device_group,db}
# 	 * @return data (TemplateGroupDeviceOutBase)
# 	 */
@router.post('/get_device_group/', response_model=schemas.TemplateGroupDeviceOutBase)
def get_group_device(id_device_group: Optional[int] = Body(embed=True), db: Session = Depends(get_db) ):
    try:
        id=id_device_group
        device_group_query = db.query(models.Device_group).filter(
        models.Device_group.id == id).first()
        if not device_group_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Device with id: {id} does not exist")
        # print(device_group_query.__dict__)
        config_point = db.query(models.Config_information).filter(models.Config_information.status 
                                                                                   == 1).all()
        data_type=[]
        data_type = [item.__dict__ for item in config_point if item.id_type == 1]
        byte_order=[]
        byte_order = [item.__dict__ for item in config_point if item.id_type == 2]
        point_unit=[]
        point_unit = [item.__dict__ for item in config_point if item.id_type == 3]
    
        point_list=[]
        register_list=[]
        if hasattr(device_group_query, 'templates_library'):
            templates_library=device_group_query.templates_library
            if hasattr(templates_library, 'point_list'):     
                # point_list =[item.__dict__ for item in templates_library.point_list]
                point_list =templates_library.point_list
                print(point_list[0].config)
            if hasattr(templates_library, 'register_list'):
                register_list =templates_library.register_list

        return {
            "device_group": device_group_query,
            "data_type":data_type,
            "byte_order":byte_order,
            "point_unit":point_unit,
            "point_list":point_list,
            "register_list":register_list
        }
    except Exception as err: 
        print('Error : ',err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not have data")

# Describe functions before writing code
# /**
# 	 * @description get each point
# 	 * @author vnguyen
# 	 * @since 18-12-2023
# 	 * @param {info_point,db}
# 	 * @return data (PointTemplateOutBase)
# 	 */
@router.post('/get_each_point/', response_model=schemas.PointTemplateOutBase)
def get_each_point(info_point: schemas.PointInfoTemplateBase,db: Session = Depends(get_db) ):
    try:
        point_query = db.query(models.Point_list).filter(
        models.Point_list.id == info_point.id_point)
        
        result_point=point_query.first()
        if not result_point:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                               detail=f"Point with id: {id} does not exist")
        config_point = db.query(models.Config_information).filter(models.Config_information.status 
                                                                                   == 1).all()
        data_type=[]
        data_type = [item.__dict__ for item in config_point if item.id_type == 1]
        byte_order=[]
        byte_order = [item.__dict__ for item in config_point if item.id_type == 2]
        point_unit=[]
        point_unit = [item.__dict__ for item in config_point if item.id_type == 3]
        
        type_point=[]
        type_point = [item.__dict__ for item in config_point if item.id_type == 15 and item.type == 1]
        type_class=[]
        type_class = [item.__dict__ for item in config_point if item.id_type == 15 and item.type == 2]
        
        # result_point["type_units_list"]=point_unit
        
        return schemas.PointTemplateOutBase(**result_point.__dict__,
                                            type_units_list=point_unit,
                                            type_datatype_list=data_type,
                                            type_byteorder_list=byte_order,
                                            type_point_list=type_point,
                                            type_class_list=type_class,
                                            )
    except Exception as err: 
        print('Error : ',err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not have data")
# Describe functions before writing code
# /**
# 	 * @description edit each point
# 	 * @author vnguyen
# 	 * @since 29-12-2023
# 	 * @param {info_point,db}
# 	 * @return data (PointOutBase)
# 	 */
@router.post('/edit_each_point/', response_model=schemas.PointOutBase)
def edit_each_point(info_point: schemas.PointUpdateBase,db: Session = Depends(get_db) ):
    try:
        point_query = db.query(models.Point_list).filter(
        models.Point_list.id == info_point.id).filter(
        models.Point_list.id_template == info_point.id_template)
        result_point=point_query.first()
        if not result_point:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                               detail=f"Point with id: {id} does not exist")
        mode_modbus_equation=db.query(models.Config_information).filter(
        models.Config_information.id == info_point.equation).first()
        if not hasattr(mode_modbus_equation, 'value'):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                               detail=f"Config Device modbus or virtual with value: {info_point.equation} does not exist")
        equation=mode_modbus_equation.value
        print(f'equation: {equation}')
        id_template=info_point.id_template
        update_point=dict()
        match equation:
            # Mode Modbus register
            case 1:
                update_point= dict(**info_point.dict())
            # Mode Equation
            case 2:
                update_point=dict(  equation=info_point.equation,
                                    name=info_point.name,
                                    nameedit=info_point.nameedit,
                                    id_type_units=info_point.id_type_units,
                                    unitsedit=info_point.unitsedit,
                                  )              
            case _:
                pass
        print(f'update_point: {update_point}')
        point_query.update(update_point)
        restart_pm2_change_template(id_template,db)
        db.commit()  
        return result_point
    except exc.SQLAlchemyError as err:
        print('Error : ',err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not have data")

# Describe functions before writing code
# /**
# 	 * @description change number point
# 	 * @author vnguyen
# 	 * @since 08-01-2024
# 	 * @param {PointChangeNumberBase,db}
# 	 * @return data (PointBase)
# 	 */
@router.post('/change_number_point/', response_model=list[schemas.PointBase])
def change_number_point(change_number_point: schemas.PointChangeNumberBase, db: Session = Depends(get_db) ):
    try:
        number_point=change_number_point.number_point
        id_template=change_number_point.id_template
        point_query = db.query(models.Point_list).filter(models.Point_list.id_template == id_template)
        result_point=point_query.all()
        if result_point and len(result_point)>0 :
            count_point=len(result_point)
            if number_point<count_point:
                print(f'----- Delete point -----')
                # delete
                array_delete=result_point[number_point:count_point]
                for item in array_delete:
                    print(f'Delete Id: {item.id}')
                    result=point_query.filter(
                                models.Point_list.id == item.id).delete(synchronize_session=False)
                    db.flush()
                    restart_pm2_change_template(id_template,db)
                    db.commit()
                point_query = db.query(models.Point_list).filter(models.Point_list.id_template == id_template)
                result_point=point_query.all()
                return result_point
            elif number_point==count_point:
                print(f'----- Keep point -----')
                # no do
                point_query = db.query(models.Point_list).filter(models.Point_list.id_template == id_template)
                result_point=point_query.all()
                return result_point
            else:
                print(f'----- Insert point -----')
                config_info_query = db.query(models.Config_information).filter(models.Config_information.status == 1)
                result_config_info=config_info_query.all()
                
                name=""
                nameedit=False
                id_type_units=[item.__dict__ for item in result_config_info if item.namekey == "(No units)" and item.id_type==3][0]['id']
                unitsedit=False
                id_equation=[item.__dict__ for item in result_config_info if item.namekey == "Modbus register" and item.id_type==15][0]['id']
                id_config=[item.__dict__ for item in result_config_info if item.namekey == "Input" and item.id_type==15][0]['id']
                register=0
                id_type_datatype=[item.__dict__ for item in result_config_info if item.namekey == "Short" and item.id_type==1][0]['id']
                id_type_byteorder=[item.__dict__ for item in result_config_info if item.namekey == "normal" and item.id_type==2][0]['id']
                slope=1
                slopeenabled=False
                offset=0
                offsetenabled=False
                multreg=0
                multregenabled=False
                userscaleenabled=False
                invalidvalue=65535
                invalidvalueenabled=False
                extendednumpoints=0
                extendedregblocks=0
                constants=0
                function=""
                # add
                number_point_add=number_point-count_point
                new_point_list=[]
                
                for item in range(number_point_add):
                    new_point = models.Point_list(
                                id_template=id_template,
                                name=name,
                                nameedit=nameedit,
                                id_type_units=id_type_units,
                                unitsedit=unitsedit,
                                equation=id_equation,
                                config=id_config,
                                register=register,
                                id_type_datatype=id_type_datatype,
                                id_type_byteorder = id_type_byteorder,
                                slope =slope,
                                slopeenabled = slopeenabled,
                                offset = offset,
                                offsetenabled = offsetenabled,
                                multreg = multreg,
                                multregenabled =multregenabled ,
                                userscaleenabled = userscaleenabled,
                                invalidvalue = invalidvalue,
                                invalidvalueenabled = invalidvalueenabled,
                                extendednumpoints = extendednumpoints,
                                extendedregblocks =extendedregblocks ,
                                status = 1,
                                function=function ,
                                constants=constants
                                )
                    new_point_list.append(new_point)
                
                db.add_all(new_point_list)
                db.flush()
                device_point_list_query = db.query(models.Device_point_list).filter(models.Device_point_list.id_template == id_template)
                result_device_point_list=device_point_list_query.all()
                
                if result_device_point_list:
                    # check number device
                    device_list=list(set([item.id_device_list for item in result_device_point_list]))
                    insert_device_point_list=[]
                    for item_point in new_point_list:
                        for item_device in device_list:
                            id_device_group=[item.__dict__ for item in result_device_point_list 
                                            if item.id_device_list == item_device][0]['id_device_group']
                            insert_device_point_list.append(models.Device_point_list(id_template=id_template,
                                                                            id_device_group=id_device_group,
                                                                            id_device_list=item_device,
                                                                            id_point_list=item_point.id))
                    if insert_device_point_list:
                        db.add_all(insert_device_point_list)
                restart_pm2_change_template(id_template,db)
                db.commit()
                point_query = db.query(models.Point_list).filter(models.Point_list.id_template == id_template)
                result_point=point_query.all()
                # print(result_point)
                return result_point
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not have data")
        
    except Exception as err:
        print(f'Error: {err}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not have data")
# Describe functions before writing code
# /**
# 	 * @description delete point list
# 	 * @author vnguyen
# 	 * @since 08-01-2024
# 	 * @param {id,db}
# 	 * @return data (DeviceGroupOutBase)
# 	 */
@router.post('/delete_point_list/', response_model=list[schemas.PointBase])
def delete_point_list(point_list: schemas.PointDeleteTemplateBase, db: Session = Depends(get_db) ):
    try:
        id_template=point_list.id_template
        point_query = db.query(models.Point_list).filter(models.Point_list.id_template == id_template).\
                                                filter(models.Point_list.status == 1)
        result_point=point_query.all()
        if not result_point:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Not have data")
        
        for item in point_list.id_point:
            point_query.filter(
                                models.Point_list.id == item).delete(synchronize_session=False)
        
        db.flush()
        restart_pm2_change_template(id_template,db)
        db.commit()
        return point_query.all()
    except Exception as err:
        print(f'Error: {err}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Can't delete data")
# Describe functions before writing code
# /**
# 	 * @description get register list
# 	 * @author vnguyen
# 	 * @since 10-01-2024
# 	 * @param {db}
# 	 * @return data (RegisterConfigOutBase)
# 	 */
@router.post('/get_register_list/', response_model=schemas.RegisterConfigOutBase)
def get_register_list(id_template: Optional[int] = Body(embed=True), db: Session = Depends(get_db) ):
    try:
        register_query = db.query(models.Register_block).filter(models.Register_block.id_template == id_template)
        result_register=register_query.all()
        if not result_register:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Template with id: {id_template} does not exist")
        config_register = db.query(models.Config_information).filter(models.Config_information.status 
                                                                                   == 1).all()
        type_function=[]
        type_function = [item.__dict__ for item in config_register if item.id_type == 5]
        return {
            "register_list":result_register,
            "type_function":type_function
        }
    except Exception as err: 
        print('Error : ',err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not have data")
# Describe functions before writing code
# /**
# 	 * @description edit each register
# 	 * @author vnguyen
# 	 * @since 10-01-2024
# 	 * @param {info_register,db}
# 	 * @return data (RegisterOutBase)
# 	 */
@router.post('/edit_each_register/', response_model=schemas.RegisterOutBase)
def edit_each_register(info_register: schemas.RegisterOutBase,db: Session = Depends(get_db) ):
    try:
        id=info_register.id
        id_template=info_register.id_template
        register_query = db.query(models.Register_block).filter(
        models.Register_block.id == id)
        result_register=register_query.first()
        print(result_register.__dict__)
        if not result_register:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Register with id: {id} does not exist")
        restart_pm2_change_template(id_template,db)
        register_query.update(info_register.dict())   
        db.commit()
        return result_register
    except exc.SQLAlchemyError as err:
        print('Error : ',err)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not have data")
# Describe functions before writing code
# /**
# 	 * @description edit all register
# 	 * @author vnguyen
# 	 * @since 10-01-2024
# 	 * @param {register_list,db}
# 	 * @return data (RegisterOutBase)
# 	 */
@router.post('/edit_all_register/', response_model=list[schemas.RegisterOutBase])
def edit_all_register(register_list: list[schemas.RegisterOutBase],db: Session = Depends(get_db) ):
    try:
        id_template=register_list[0].id_template

        register_query = db.query(models.Register_block).filter(
            models.Register_block.id_template == id_template)
        for item in register_list:
            register_query.filter(
            models.Register_block.id == item.id).\
                update(item.dict())
        db.commit()
        restart_pm2_change_template(id_template,db)
        return register_query
        
    except (exc.SQLAlchemyError,Exception) as err:
        print(f'Error: {err}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not have data")
# Describe functions before writing code
# /**
# 	 * @description delete register
# 	 * @author vnguyen
# 	 * @since 10-01-2024
# 	 * @param {id,db}
# 	 * @return data (RegisterOutBase)
# 	 */
@router.post('/delete_register/', response_model=list[schemas.RegisterOutBase])
def delete_register(register_list: list[schemas.RegisterOutBase], db: Session = Depends(get_db) ):
    try:
        id_template=register_list[0].id_template
        register_query = db.query(models.Register_block).filter(models.Register_block.id_template == id_template)
        result_register=register_query.all()
        if not result_register:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Template with id: {id_template} does not exist")
        
        for item in register_list:
            register_query.filter(
                                models.Register_block.id == item.id).delete(synchronize_session=False)
        
        restart_pm2_change_template(id_template,db)
        db.commit()
        return register_query.all()
    except (exc.SQLAlchemyError,Exception) as err:
        print(f'Error: {err}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Can't delete data")