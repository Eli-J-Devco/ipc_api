# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
# path=path_directory_relative("ipc_api") # name of project
# sys.path.append(path)
import os
import sys
from pathlib import Path

sys.path.append( (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))
# import models
from configs.config import Config

# from utils.logger_manager import setup_logger

# from database.db import engine
# LOGGER = setup_logger(module_name='API')
API_DOCS_USERNAME = Config.API_DOCS_USERNAME
API_DOCS_PASSWORD = Config.API_DOCS_PASSWORD
API_PORT= Config.API_PORT

print(f'API_DOCS_USERNAME: {API_DOCS_USERNAME}')
import http
# import logging
import secrets
import time

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (get_redoc_html, get_swagger_ui_html,
                                  get_swagger_ui_oauth2_redirect_html)
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
# from routers import deviceControl as deviceControl_router
# from routers import (auth, device_group, device_list, ethernet, project, rs485,
#                      site_information, template, upload_channel, user)
# -------------------------------------------------------------
from routers import auth as auth_router
from routers import deviceGroup as deviceGroup_router
from routers import deviceList as deviceList_router
from routers import ethernet as ethernet_router
from routers import project as project_router
from routers import rs485 as rs485_router
from routers import siteInfo as siteInfo_router
from routers import template as template_router
from routers import uploadChannel as uploadChannel_router
from routers import user as user_router
# -------------------------------------------------------------
from starlette import status
from starlette.exceptions import ExceptionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# from utils import LOGGER, path_directory_relative

# models.Base.metadata.create_all(bind=engine)
# class PartnerAvailabilityMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request, call_next):
#         raise CustomException(
#             status.HTTP_503_SERVICE_UNAVAILABLE, 'Partner services is unavailable.'
#         )
#         return await call_next(request)
app = FastAPI(
    title="FastAPI",
    description="IPC SCADA",
    version="2023.10.0",
    contact={
        "name":"vnuyen",
        "email":"vnguyen@nwemon.com"
        },
    docs_url=None,
    redoc_url=None,
    openapi_url = None,
    )

origins = [
    "*"
]

security = HTTPBasic()
# async def log_request_middleware(request: Request, call_next):
#     """
#     This middleware will log all requests and their processing time.
#     E.g. log:
#     0.0.0.0:1234 - GET /ping 200 OK 1.00ms
#     """
#     # logger.debug("middleware: log_request_middleware")
#     url = f"{request.url.path}?{request.query_params}" if request.query_params else request.url.path
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = (time.time() - start_time) * 1000
#     formatted_process_time = "{0:.2f}".format(process_time)
#     host = getattr(getattr(request, "client", None), "host", None)
#     port = getattr(getattr(request, "client", None), "port", None)
#     try:
#         status_phrase = http.HTTPStatus(response.status_code).phrase
#     except ValueError:
#         status_phrase=""
#     # logger.info(f'{host}:{port} - "{request.method} {url}" {response.status_code} {status_phrase} {formatted_process_time}ms')
#     return response
# app.middleware("http")(log_request_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_router.router)
app.include_router(auth_router.router)
app.include_router(template_router.router)
app.include_router(deviceGroup_router.router)
app.include_router(deviceList_router.router)

app.include_router(ethernet_router.router)
app.include_router(rs485_router.router)
app.include_router(siteInfo_router.router)
app.include_router(uploadChannel_router.router)
app.include_router(project_router.router)
# app.include_router(deviceControl_router.router)
# 

# class CustomException(Exception):
#     def __init__(self, code: int, message: str):
#         self.code = code
#         self.message = message
# @app.exception_handler(CustomException)
# async def custom_exception_handler(request: Request, exc: CustomException):
#     return JSONResponse(
#         status_code=exc.code,
#         content={"message": f"Exception Occurred! Reason -> {exc.message}"},
#     )
# Describe functions before writing code
# /**
# 	 * @description get current username
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {credentials}
# 	 * @return data (credentials.username)
# 	 */

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
# @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
# async def swagger_ui_redirect():
#     return get_swagger_ui_oauth2_redirect_html()

# Describe functions before writing code
# /**
# 	 * @description api doc
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {}
# 	 * @return data ()
# 	 */
@app.get("/docs", include_in_schema=False)
async def get_swagger_documentation(username: str = Depends(get_current_username)):
    return get_swagger_ui_html(openapi_url="/openapi.json",
                                title="docs",
                                # oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
                                swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
                                swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
                               )
# Describe functions before writing code
# /**
# 	 * @description api redoc
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {}
# 	 * @return data ()
# 	 */

@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation(username: str = Depends(get_current_username)):
    return get_redoc_html(openapi_url="/openapi.json", 
                          title="docs",
                          redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
                        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
                        with_google_fonts=True
                          )
    # return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")
# Describe functions before writing code
# /**
# 	 * @description openapi.json
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {}
# 	 * @return data ()
# 	 */

@app.get("/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(get_current_username)):
    return get_openapi( 
        title=app.title, 
        version=app.version, 
        contact=app.contact, 
        description=app.description,
        routes=app.routes)
# Describe functions before writing code
# /**
# 	 * @description root
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {}
# 	 * @return data ()
# 	 */
@app.get("/")
def root():
    return {"message": "Hello "}
@app.on_event("startup")
async def startup():
    print("startup ---------")
    # LOGGER.info("--- Start up App ---")

    
@app.on_event("shutdown")
async def shutdown():
    print("shutdown ---------")
    # LOGGER.error("--- Shutdown App ---")


if __name__ == '__main__':
    # uvicorn.run(app, port=8080, host='0.0.0.0')
    uvicorn.run("__main__:app", host="0.0.0.0", port=API_PORT, reload=True, workers=2)
    # uvicorn.run("__main__:app", host="0.0.0.0", port=API_PORT, reload=False, workers=2)