import secrets
import sys

import models
from database import engine
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from routers import auth, device_list, ethernet, rs485, user
from utils import path_directory_relative

path=path_directory_relative("ipc_api") # name of project
sys.path.append(path)
from config import Config

API_DOCS_USERNAME = Config.API_DOCS_USERNAME
API_DOCS_PASSWORD = Config.API_DOCS_PASSWORD

models.Base.metadata.create_all(bind=engine)

app = FastAPI(  title="FastAPI",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url = None,)

origins = ["*"]
security = HTTPBasic()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(device_list.router)
app.include_router(ethernet.router)
app.include_router(rs485.router)

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, API_DOCS_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, API_DOCS_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/docs", include_in_schema=False)
async def get_swagger_documentation(username: str = Depends(get_current_username)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation(username: str = Depends(get_current_username)):
    return get_redoc_html(openapi_url="/openapi.json", title="docs")


@app.get("/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(get_current_username)):
    return get_openapi(title=app.title, version=app.version, routes=app.routes)
@app.get("/")
def root():
    return {"message": "Hello World pushing out to ubuntu"}
