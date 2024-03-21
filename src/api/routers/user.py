# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import copy
import datetime
import json
import os
import random
import secrets
import string
import sys
from typing import Optional

from fastapi import (APIRouter, Body, Depends, FastAPI, HTTPException,
                     Response, status)
# from psycopg2 import sql
# from sqlalchemy.sql import text
from fastapi.responses import JSONResponse
from sqlalchemy import (Integer, MetaData, String, Table, and_, bindparam, exc,
                        func, insert, join, literal_column, select, text,
                        union, union_all)
from sqlalchemy.orm import Session, aliased

sys.path.append((lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))

import api.domain.deviceList.models as deviceList_models
import api.domain.deviceList.schemas as deviceList_schemas
# from api.domain.user import models, schemas
import api.domain.user.models as user_models
import api.domain.user.schemas as user_schemas
import utils.oauth2 as oauth2
from configs.config import *
from database.db import engine, get_db
from utils.libCom import cov_xml_sql
from utils.passwordHasher import convert_binary_auth, hash, verify

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

account_status = {
     "active": 1,
     "inactive": 0,
}
# /users/
# /users

# Describe functions before writing code
# /**
# 	 * @description create user
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {UserCreate,db}
# 	 * @return data (UserStateOut)
# 	 */
@router.post("/create_user", status_code=status.HTTP_201_CREATED, response_model=user_schemas.UserStateOut)
def create_user(user: user_schemas.UserRoleCreate, db: Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user)):
    
    
    user_query = db.query(user_models.User).filter(user_models.User.email == user.email).first()
    if user_query:
        return {
            "status": "success",
            "code": "100",
            "desc":"User already created"
        }
    else:
        hashed_password = hash(user.password)
        user.password = hashed_password
        now = datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        # new_user = models.User(date_joined=now,
        #                         last_login=now, **user.dict())
        new_user = user_models.User(
                                # fullname=user.fullname,
                                first_name=user.first_name,
                                last_name=user.last_name,
                                email=user.email,
                                password=user.password,
                                phone=user.phone,
                                # id_language=user.id_language,
                                # date_joined=now,
                                # last_login=now,
                                create_date=now,
                                last_login=now,     
                                )
        try:
            db.add(new_user)
            db.flush()
            if not hasattr(new_user, 'id'):
                return {
                "status": "error",
                "code": "300",
                "desc":""
                }
            # 
            new_user_role_list=[]
            for item in user.role:
                new_user_role=user_models.User_role_map( id_user=new_user.id,
                                                    id_role=item.id,     
                                                    )
                new_user_role_list.append(new_user_role)
            if new_user_role_list:
                db.add_all(new_user_role_list)
                db.flush()
            # 
            db.commit()
            db.refresh(new_user)
            return {
                "status": "success",
                "code": "100",
                "desc":""
            }
        except exc.SQLAlchemyError as err:
            db.rollback()
            return {
                "status": "error",
                "code": "300",
                "desc":""
                }
# Describe functions before writing code
# /**
# 	 * @description manager user
# 	 * @author vnguyen
# 	 * @since 26-12-2023
# 	 * @param {UserCreate,db}
# 	 * @return data (new_user)
# 	 */
@router.post("/all_user", status_code=status.HTTP_201_CREATED, response_model=user_schemas.UserRoleOut)
def get_all_user(page:int, limit:int, status: int | None = None, db: Session = Depends(get_db), 
                current_user: int = Depends(oauth2.get_current_user)):
        try:
            if status is not None:
                user_query = db.query(user_models.User).filter(user_models.User.status == status)
            else:
                user_query = db.query(user_models.User)
            result_user=user_query.offset(page).limit(limit).all()
            if not result_user:
                return JSONResponse(status_code=status.HTTP_204_NO_CONTENT,
                                    content=f"User empty")
            user_list=user_schemas.UserRoleOut(total=user_query.count(), data=[])
            for item_user in result_user:
                result_user_role = db.query(user_models.User_role_map).filter(
                user_models.User_role_map.id_user == item_user.id).all()
                role_list=[]
                for item_role in result_user_role:
                    role_list.append({
                            "id": item_role.role.id,
                            "name": item_role.role.name,
                    })
                # user_schemas.UserOut(**item_user.__dict__, role=role_list)
                user_list.data.append(user_schemas.UserOut(**item_user.__dict__, role=role_list))
            return user_list
        except exc.SQLAlchemyError as err:
            db.rollback()
            return {
                "status": "error",
                "code": "300",
                "desc":""
                }
# Describe functions before writing code
# /**
# 	 * @description change password
# 	 * @author vnguyen
# 	 * @since 25-12-2023
# 	 * @param {UserChangePassword,db}
# 	 * @return data (UserStateOut)
# 	 */
@router.post("/change_password", response_model=user_schemas.UserStateOut)
def change_password(user_credentials: user_schemas.UserChangePassword, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
        try:
            print(f'current_user.id: {current_user.id}')
            user_query = db.query(user_models.User).filter(
                user_models.User.id == current_user.id)
            result_user=user_query.first()
            if not result_user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"user with id: { current_user.id} does not exist")
            if not verify(user_credentials.old_password, result_user.password):
                raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
            hashed_password = hash(user_credentials.new_password)
            user_query.update(dict(password=hashed_password,), synchronize_session=False)
            db.commit()
            # db.refresh(new_user)
            return {
                "status": "success",
                "code": "100",
                "desc":""
            }
        except exc.SQLAlchemyError as err:
            db.rollback()
            return {
                "status": "error",
                "code": "300",
                "desc":""
                }
# Describe functions before writing code
# /**
# 	 * @description reset password
# 	 * @author vnguyen
# 	 * @since 25-12-2023
# 	 * @param {UserChangePassword,db}
# 	 * @return data (UserStateOut)
# 	 */
@router.post("/reset_password", response_model=user_schemas.UserResetPassword)
def reset_password(username: Optional[str] = Body(embed=True), db: Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user)):
    
        try:
            # print(f'current_user.id: {current_user.id}')
            user_query = db.query(user_models.User).filter(
                user_models.User.email == username)
            result_user=user_query.first()
            if not result_user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"user with email: { username} does not exist")
 
            # using random.choices()
            # generating random strings
            required_letters = string.ascii_letters + string.digits + string.punctuation + string.ascii_uppercase + string.ascii_lowercase
            new_password = ''.join(secrets.choice(required_letters) for i in range(20))
            
            hashed_password = hash(new_password)
            user_query.update(dict(password=hashed_password,), synchronize_session=False)
            db.commit()
            return {
                "status": "success",
                "code": "100",
                "desc":"",
                "password":new_password
            }
        except exc.SQLAlchemyError as err:
            db.rollback()
            return {
                "status": "error",
                "code": "300",
                "desc":""
                }
# Describe functions before writing code
# /**
# 	 * @description delete user
# 	 * @author vnguyen
# 	 * @since 26-12-2023
# 	 * @param {id}
# 	 * @return data (RoleScreenState)
# 	 */
@router.post("/delete/user/", response_model=user_schemas.UserStateOut)
def delete_user(id: Optional[int] = Body(embed=True), db: Session = Depends(get_db),  current_user: int = Depends(oauth2.get_current_user)):
    

    try:
        user_query = db.query(user_models.User).filter(
        user_models.User.id == id)
        result_role=user_query.first()
        if not result_role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with id: {id} does not exist")
            
        user_query.delete(synchronize_session=False)
        db.commit()
        return {
                    "status": "success",
                    "code": "100",
                    "desc":""
                }
    except exc.SQLAlchemyError as err:
        print(err)
        return {
                    "status": "error",
                    "code": "300",
                    "desc":""
                    }
# Describe functions before writing code
# /**
# 	 * @description get user
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,db}
# 	 * @return data (new_user)
# 	 */
@router.post('/only_user', response_model=user_schemas.UserRoleOut)
# def get_only_user(id: Optional[int] = Body(embed=True), db: Session = Depends(get_db),  current_user: int = Depends(oauth2.get_current_user)):
def get_only_user(id: Optional[int] = Body(embed=True), db: Session = Depends(get_db),  current_user: int = Depends(oauth2.get_current_user)):
    # print(f'id: {id}')
    # ----------------------
    user = db.query(user_models.User).filter(user_models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")
    result_user_role = db.query(user_models.User_role_map).filter(
        user_models.User_role_map.id_user == user.id).all()
    role_list=[]
    for item_role in result_user_role:
         if hasattr(item_role, 'role'):
             role_list.append({
                    "id": item_role.role.id,
                    "name": item_role.role.name,
             })
    
   
    result={**user.__dict__,"role":role_list}
   
    
    # ----- only one row -----
    # users=user.__dict__
    # print(f'{users}')
    # ---- good------------------
    # result = db.execute(
    # text(f'select * from user')).all()
    # results_dict = [row._asdict() for row in result]
    # print(f'{results_dict}')
    
    # if id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail="Not authorized to perform requested action")
    
    # ----------------------
    

    return result

# Describe functions before writing code
# /**
# 	 * @description update user
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,UserCreate,db,current_user}
# 	 * @return data (UserOut)
# 	 */
@router.post("/update_user/", response_model=user_schemas.UserStateOut)
def update_user( updated_user: user_schemas.UserUpdate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    try:
        id=updated_user.id
        user_query = db.query(user_models.User).filter(user_models.User.id == id)
        result_user=user_query.first()
        
        if not result_user:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail=f"User with id: { updated_user.id} does not exist")
        
        user_query.update(updated_user.model_dump(), synchronize_session=False)
        user_role_query= db.query(user_models.User_role_map).filter(user_models.User_role_map.id_user == id)
        result_delete=user_role_query.delete(synchronize_session=False)
        new_user_role_list=[]
        for item in updated_user.role:
            new_user_role=user_models.User_role_map( id_user=id,
                                                id_role=item.id,     
                                                )
            new_user_role_list.append(new_user_role)
        if new_user_role_list:
            db.add_all(new_user_role_list)
            db.flush()
        # 
        db.commit()
        # db.refresh(new_user)
        # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
        #                (post.title, post.content, post.published, str(id)))

        # updated_post = cursor.fetchone()
        # conn.commit()
        # current_user.id
        # print('update ------------------------')
        # id=current_user.id
        return {
                        "status": "success",
                        "code": "100",
                        "desc":"",
                        
                    }
    except exc.SQLAlchemyError as err:
            db.rollback()
            return {
                "status": "error",
                "code": "300",
                "desc":""
                }
# Describe functions before writing code
# /**
# 	 * @description active user
# 	 * @author vnguyen
# 	 * @since 26-12-2023
# 	 * @param {UserActive,db}
# 	 * @return data (UserStateOut)
# 	 */
@router.post("/active_user/", response_model=user_schemas.UserStateOut)
def active_user( updated_user: user_schemas.UserActive, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    try:
        id=updated_user.id
        user_query = db.query(user_models.User).filter(user_models.User.id == id)
        result_user=user_query.first()
        
        if not result_user:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail=f"User with id: { updated_user.id} does not exist")
        user_query.update(dict(is_active=updated_user.active), synchronize_session=False)
        db.commit()
        return {
                        "status": "success",
                        "code": "100",
                        "desc":"",
                        
                    }
    except exc.SQLAlchemyError as err:
            db.rollback()
            return {
                "status": "error",
                "code": "300",
                "desc":""
                }
# Describe functions before writing code
# /**
# 	 * @description create role
# 	 * @author vnguyen
# 	 * @since 25-12-2023
# 	 * @param {}
# 	 * @return data (RoleOut)
# 	 */
@router.post("/create/role/", response_model=user_schemas.RoleCreateState)
def create_role(create_role: user_schemas.RoleCreate, db: Session = Depends(get_db), 
                current_user: int = Depends(oauth2.get_current_user) ):
    
    try:
        new_role = user_models.Role( name=create_role.name,
                            description=create_role.description,
                            )
        db.add(new_role)
        db.flush()
        # print(new_role.__dict__)
        if not hasattr(new_role, 'name'):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Role create error")
        # db.query(deviceList_models.Device_list)
        id=new_role.id
        
        # stmt = "INSERT INTO  `role_screen_map` (id_role, id_screen, auths) SELECT :id_role, `screen`.`id`,:auths FROM `screen`"
        # result_insert =db.execute(text(stmt),{"id_role": id,"auths":0})
        param={
            "id_role":id,
            "auths":8
        }
        query_sql= cov_xml_sql("device.xml","add_role_screen",param)
        # print(f'query_sql: {query_sql}')
        result_insert =db.execute(text(query_sql))
        db.commit()
        return {
                        "status": "success",
                        "code": "100",
                        "desc":"",
                        
                    }
        # ---------------------------------------------------------------------------
        # result_mybatis=get_mybatis('/mybatis/device.xml')
                    
        # sql_insert_role_screen=result_mybatis["insert_role_screen"]
        # sql_insert_role_screen1=result_mybatis["create_new_table"]
        # sql_insert_role_screen2=result_mybatis["insert_data_fruits"]
        
        # stmt=sql_insert_role_screen2
        # print(f'stmt: {stmt}')
        # print('--------------------')
        # # result_insert =db.execute(text(pybatis(stmt,{"table_name": u'fruits'})),[
        # #                                 {"name": "sandy", "category": "Sandy Cheeks","price":11},
        # #                                 {"name": "patrick", "category": "Patrick Star","price":12}
        # #                              ])
        # result_insert =db.execute(text(sql_insert_role_screen2),[
        #                                 {"name": "sandy", "category": "Sandy Cheeks","price":11},
        #                                 {"name": "patrick", "category": "Patrick Star","price":12}
        #                              ])


        # result_insert =db.execute(text(pybatis(stmt,{"table_name": u'fruits'})))#,{"id_role": u'fruits'}
        # print(result_insert.__dict__)
        # for row in result_insert:
        #     print(row)
        # ---------------------------------------------------------------------------
        # point_query = db.query(models.Test).filter(models.Test.id == 1)
        # result=point_query.first()
        # print(result.__dict__)
        # db.commit()


        # #
        # create new table
        # db.execute(models.TableCreator("inv0111"))

        # return new_role
        # user_query = db.query(models.User_role_map).\
        # filter(models.User_role_map.id_user == 49).first()
        
        # print(f'user_query: {user_query.user.__dict__}')
        # join_Device_list_Device_group = models.Device_group.join( models.Device_list, models.Device_group.c.Id == models.Device_list.c.id_device_group)
        # stmt = select(models.Device_list,  models.Device_group).\
        #     select_from(join_Device_list_Device_group).\
        #     where(models.Device_list.c.Id == 2)
        # stmt = select(models.Device_list).where(models.Device_list.id == 2)
        
        # j = models.Device_group.join(models.Device_list,  models.Device_group.c.Id == models.Device_list.c.id_device_group)
        # u1 = aliased( models.Device_group, name="u1")
        
        
        # stmt = select(models.Device_list.id,models.Device_list.name).\
        #                                                             join_from(models.Device_list,models.Device_group).\
        #                                                             join_from(models.Device_group,models.Template_library).\
        #                                                             join_from(models.Template_library,models.Register_block).\
        #                                                             where(models.Device_list.id == 2)
        # stmt = select(models.Device_list.id).\
        #                                                             join(models.Device_group).\
        #                                                             join(models.Template_library).\
        #                                                             join(models.Register_block).\
        #                                                             where(models.Device_list.id == 2)
        # eval('')
        # stmt = select(  models.Device_list.id.label("id_device_list"), \
        #                 models.Template_library.id.label("id_template"),\
        #                 models.Device_list.id_device_group,\
        #                 models.Register_block.id.label("id_register_block")).\
        #                 join_from(models.Device_list,models.Device_group).\
        #                 join_from(models.Device_group,models.Template_library).\
        #                 join_from(models.Template_library,models.Register_block).\
        #                 where(models.Device_list.id == 6)
        # # eval(fun())
        
        # insert_stmt = insert(models.Device_register_block).from_select(["id_device_list",
        # "id_template",
        # "id_device_group",
        # "id_register_block"],stmt)
        
        # query1 = select(models.Device_list).where(models.Device_list.id == 2)
        # query2 = select(models.Device_list).where(models.Device_list.id == 3)
        # query3 = select(models.Device_list).where(models.Device_list.id == 4)
        # all_queries = [query1, query2, query3]
        # query = union(*all_queries)
        
        
        # print(query)
        
        
        # result=db.execute(query).all()
        # print(result)
        # result=db.execute(insert_stmt)
        # print(insert_stmt)
        
        # db.commit()
        # print(result)
        # for item in result:
        #     print(f'{item}')
        # print(f'item: {item.id} {item.name}')
        # table = Table('device_list', models.Base.metadata, autoload=True,
        #                autoload_with=engine)
        # query = table.select()    
        # print(query)    
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        #                        detail=f"Role create error")
    except exc.SQLAlchemyError as err:
        print(f'err: {err}')
        return      {
                    "status": "error",
                    "code": "300",
                    "desc":""
                    }

# Describe functions before writing code
# /**
# 	 * @description delete role
# 	 * @author vnguyen
# 	 * @since 25-12-2023
# 	 * @param {id}
# 	 * @return data (RoleScreenState)
# 	 */
@router.post("/delete/role/", response_model=user_schemas.RoleScreenState)
def delete_role(id: Optional[int] = Body(embed=True), db: Session = Depends(get_db),  current_user: int = Depends(oauth2.get_current_user)):
    

    try:
        is_role_in_user_query = db.query(user_models.User_role_map).filter(user_models.User_role_map.id_role == id)
        result_role_in_user=is_role_in_user_query.first()
        if result_role_in_user:
            return JSONResponse(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                content=f"Role with id: {id} is in use")
        role_query = db.query(user_models.Role).filter(
        user_models.Role.id == id).filter(
        user_models.Role.status == 1)
        result_role=role_query.first()
        if not result_role:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Role with id: {id} does not exist")
            
        role_query.delete(synchronize_session=False)
        db.commit()
        return {
                    "status": "success",
                    "code": "100",
                    "desc":""
                }
    except Exception as err:
        print(err)
        return      {
                    "status": "error",
                    "code": "300",
                    "desc":""
                    }
# Describe functions before writing code
# /**
# 	 * @description update role
# 	 * @author vnguyen
# 	 * @since 25-12-2023
# 	 * @param {RoleUpdate}
# 	 * @return data (RoleScreenState)
# 	 */
@router.post("/update/role/", response_model=user_schemas.RoleScreenState)
def update_role(update_role: user_schemas.RoleUpdate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user) ):
    

    try:
        role_query = db.query(user_models.Role).filter(
        user_models.Role.id == update_role.id).filter(
        user_models.Role.status == 1)
        result_role=role_query.first()
        if not result_role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Role with id: {id} does not exist")
            
        role_query.update(update_role.model_dump(),synchronize_session=False)
        db.commit()
        return {
                    "status": "success",
                    "code": "100",
                    "desc":""
                }
    except Exception as err:
        print(err)
        return      {
                    "status": "error",
                    "code": "300",
                    "desc":""
                    }
# Describe functions before writing code
# /**
# 	 * @description create role screen
# 	 * @author vnguyen
# 	 * @since 25-12-2023
# 	 * @param {RoleScreenUpdate}
# 	 * @return data (RoleScreenState)
# 	 */
@router.post("/update/role_screen/", response_model=user_schemas.RoleScreenState)
def update_role_screen(update_role_screen: user_schemas.RoleScreenUpdate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user) ):
    try:
        role_screen_query = db.query(user_models.Role_screen_map).filter(
        user_models.Role_screen_map.id_role == update_role_screen.id_role).filter(
        user_models.Role_screen_map.status == 1)
        result_role=role_screen_query.all()
        if not result_role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Role with id: {id} does not exist")
        for item in update_role_screen.role_screen:
            role_screen_query.filter(user_models.Role_screen_map.id_role == 
                                         update_role_screen.id_role).filter(user_models.Role_screen_map.id_screen == 
                                         item.id_screen).update(dict(auths=item.auth))
        db.commit()
        return {
                    "status": "success",
                    "code": "100",
                    "desc":""
                }
    except Exception as err:
        print(err)
        return  {
                    "status": "error",
                    "code": "300",
                    "desc":""
                    }
# Describe functions before writing code
# /**
# 	 * @description get role screen
# 	 * @author vnguyen
# 	 * @since 25-12-2023
# 	 * @param {RoleScreenUpdate}
# 	 * @return data (RoleScreenState)
# 	 */
@router.post("/get/role_screen/", response_model=list[user_schemas.RoleScreenOut])
def get_role_screen(id_role: Optional[int] = Body(embed=True), db: Session = Depends(get_db),  
                    current_user: int = Depends(oauth2.get_current_user) ):
    try:
        role_screen_query = db.query(user_models.Role_screen_map).filter(
        user_models.Role_screen_map.id_role ==id_role).filter(
        user_models.Role_screen_map.status == 1)
        result_role=role_screen_query.all()
        if not result_role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Role with id: {id} does not exist")
        result=[]
        for item in result_role:
            new_item={
                "id_role":item.id_role,
                "id_screen":item.id_screen,
                "auth":item.auths,
                "screen_name":item.screen.screen_name,
            }
            result.append(new_item)
        
        return result
    except Exception as err:
        # print(err)
        return      {
                    "status": "error",
                    "code": "300",
                    "desc":""
                    }
        
# Describe functions before writing code
# /**
# 	 * @description get all role
# 	 * @author vnguyen
# 	 * @since 26-12-2023
# 	 * @param {db}
# 	 * @return data (RoleOut)
# 	 */
@router.post('/all_role', response_model=list[user_schemas.RoleOut])
def get_all_role( db: Session = Depends(get_db),  current_user: int = Depends(oauth2.get_current_user)):
    # print(f'id: {id}')
    # ----------------------
    result_role = db.query(user_models.Role).filter(user_models.Role.status == 1).all()
    if not result_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Role empty")
   

    return result_role

