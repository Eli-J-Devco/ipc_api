# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime
import json
from typing import Optional

import models
import oauth2
# from model import auth_user
import schemas
import utils
from database import get_db
from fastapi import (APIRouter, Body, Depends, FastAPI, HTTPException,
                     Response, status)
from sqlalchemy import exc
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

# /users/
# /users

# Describe functions before writing code
# /**
# 	 * @description create user
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {UserCreate,db}
# 	 * @return data (new_user)
# 	 */
@router.post("/create_user", status_code=status.HTTP_201_CREATED, response_model=schemas.UserStateOut)
def create_user(user: schemas.UserRoleCreate, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.email == user.email).first()
    if user_query:
        return {
            "status": "success",
            "code": "100",
            "desc":"User already created"
        }
    else:
        hashed_password = utils.hash(user.password)
        user.password = hashed_password
        now = datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        # new_user = models.User(date_joined=now,
        #                         last_login=now, **user.dict())
        new_user = models.User(fullname=user.fullname,
                                email=user.email,
                                password=user.password,
                                phone=user.phone,
                                id_language=user.id_language,
                                date_joined=now,
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
                new_user_role=models.User_role_map( id_user=new_user.id,
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
# 	 * @description get user
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,db}
# 	 * @return data (new_user)
# 	 */
@router.post('/only_user', response_model=schemas.UserRoleOut)
# def get_only_user(id: Optional[int] = Body(embed=True), db: Session = Depends(get_db),  current_user: int = Depends(oauth2.get_current_user)):
def get_only_user(id: Optional[int] = Body(embed=True), db: Session = Depends(get_db)):
    # print(f'id: {id}')
    # ----------------------
    user = db.query(models.User).filter(models.User.id == id).first()
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
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")

    return user

# Describe functions before writing code
# /**
# 	 * @description update user
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,UserCreate,db,current_user}
# 	 * @return data (UserOut)
# 	 */
@router.post("/update/{id}", response_model=schemas.UserOut)
def update_user(id: int, updated_user: schemas.UserCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
    #                (post.title, post.content, post.published, str(id)))

    # updated_post = cursor.fetchone()
    # conn.commit()

    user_query = db.query(models.User).filter(models.User.id == id)

    user = user_query.first()

    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id: {id} does not exist")


    user_query.update(updated_user.dict(), synchronize_session=False)

    db.commit()

    return user_query.first()
# Describe functions before writing code
# /**
# 	 * @description get all role
# 	 * @author vnguyen
# 	 * @since 22-12-2023
# 	 * @param {}
# 	 * @return data (RoleOut)
# 	 */
@router.post("/role/", response_model=list[schemas.RoleOut])
def get_role( db: Session = Depends(get_db), ):
    role_query = db.query(models.Role)
    role = role_query.all()
    if role == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Role empty")
    return role
@router.post("/role_screen/", response_model=list[schemas.RoleScreenBase])
def get_role_screen(id: Optional[int] = Body(embed=True), db: Session = Depends(get_db), ):
    role_query = db.query(models.Role_screen_map).filter(models.Role_screen_map.id_role == id)

    role = role_query.all()
    print(role[0].__dict__)
    print(role[0].screen.__dict__)
    if role == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Role empty")
    return role
