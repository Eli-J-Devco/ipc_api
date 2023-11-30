# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import database
import models
import oauth2
import schemas
import utils
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.orm import Session

router = APIRouter(tags=['Authentication'])

# Describe functions before writing code
# /**
# 	 * @description get device list
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {user_credentials,db}
# 	 * @return data (Token)
# 	 */ 
@router.post('/login/', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    print(user_credentials.username)

    # user = db.execute(
    #     text("SELECT * FROM user"))
    # columns = [desc[0] for desc in db.description]
    # print(columns)
    # results = []
    # print(posts)
    # for users in user:

    #     row = dict(zip(columns, users))
    #     result.append(row)
    # print(results)
    # print(auth_user.User)
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    # create a token
    # return token

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
