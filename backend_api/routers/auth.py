from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
# from .. import database, schemas, models, utils, oauth2
import models
# from model import auth_user
import schemas
import oauth2
import database
import utils
router = APIRouter(tags=['Authentication'])


@router.post('/login', response_model=schemas.Token)
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
