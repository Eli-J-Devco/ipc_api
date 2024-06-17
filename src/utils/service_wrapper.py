# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import json
import logging
import types
from typing import Callable, Tuple, Any, Dict, Coroutine

from fastapi.responses import JSONResponse
from fastapi import status, HTTPException
from pydantic.main import BaseModel
from starlette.responses import JSONResponse


class ServiceWrapper:
    @staticmethod
    def async_wrapper(func):
        """
        Wrapper for async function
        :author: nhan.tran
        :date: 20-05-2024
        :param func:
        :return: JSONResponse
        """
        async def wrapper(*args, **kwargs) -> JSONResponse:
            """
            Wrapper for async function
            :author: nhan.tran
            :date: 20-05-2024
            :param args:
            :param kwargs:
            :return: JSONResponse
            """
            try:
                result = await func(*args, **kwargs)

                if isinstance(result, HTTPException):
                    raise result

                if isinstance(result, (JSONResponse, list, dict, tuple)):
                    return result

                if isinstance(result, str):
                    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": result})

                if isinstance(result, BaseModel):
                    return JSONResponse(status_code=status.HTTP_200_OK, content=result.dict(exclude_unset=True))

                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

                return result.__dict__
            except HTTPException as e:
                logging.error("====================================")
                logging.error("HTTPException: " + e.detail)
                logging.error("====================================")
                try:
                    status_code, message = e.detail.split(": ")
                    status_code = int(status_code)
                except ValueError:
                    status_code, message = e.status_code, e.detail
                return JSONResponse(status_code=int(status_code), content={"message": message})
            except Exception as e:
                logging.error("====================================")
                logging.error("Exception: " + str(e))
                logging.error("====================================")
                return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": str(e)})

        return wrapper

    @staticmethod
    def sync_wrapper(func):
        """
        Wrapper for sync function
        :author: nhan.tran
        :date: 20-05-2024
        :param func:
        :return: JSONResponse
        """
        def wrapper(*args, **kwargs) -> JSONResponse:
            """
            Wrapper for sync function
            :author: nhan.tran
            :date: 20-05-2024
            :param args:
            :param kwargs:
            :return: JSONResponse
            """
            try:
                return func(*args, **kwargs)
            except HTTPException as e:
                logging.error("HTTPException: " + e.detail)
                try:
                    status_code, message = e.detail.split(": ")
                    status_code = int(status_code)
                except ValueError:
                    status_code, message = e.status_code, e.detail

                return JSONResponse(status_code=int(status_code), content={"message": message})
            except Exception as e:
                logging.error("====================================")
                logging.error("Exception: " + str(e))
                logging.error("====================================")
                return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": str(e)})
        return wrapper
