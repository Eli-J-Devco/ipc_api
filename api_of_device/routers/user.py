# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime
import json

import models
import oauth2
# from model import auth_user
import schemas
import utils
from database import get_db
from fastapi import (APIRouter, Depends, FastAPI, HTTPException, Response,
                     status)
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
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # print(user.password)
    # hash the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    now = datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    new_user = models.User(date_joined=now,
                              last_login=now, **user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# Describe functions before writing code
# /**
# 	 * @description get user
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,db}
# 	 * @return data (new_user)
# 	 */
@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db), ):
    print(f'id: {id}')
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

    # if user.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail="Not authorized to perform requested action")

    user_query.update(updated_user.dict(), synchronize_session=False)

    db.commit()

    return user_query.first()
