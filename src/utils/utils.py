# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import base64
import datetime
import random
import secrets
import string
from re import match
from gzip import compress

from .pagination_model import PaginationResponse


def get_timedelta(value, unit) -> datetime.timedelta:
    """
    Get timedelta
    :author: nhan.tran
    :date: 20-05-2024
    :param value:
    :param unit:
    :return: datetime.timedelta
    """
    if unit == "s":
        return datetime.timedelta(seconds=value)
    if unit == "m":
        return datetime.timedelta(minutes=value)
    if unit == "h":
        return datetime.timedelta(hours=value)
    if unit == "d":
        return datetime.timedelta(days=value)
    if unit == "w":
        return datetime.timedelta(weeks=value)
    raise ValueError("Invalid unit")


def validate_email(email) -> str:
    """
    Validate email
    :author: nhan.tran
    :date: 20-05-2024
    :param email:
    :return: str
    """
    reg = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$"
    if not match(reg, email):
        raise ValueError("Invalid email")
    return email


def validate_phone(phone) -> str:
    """
    Validate phone
    :author: nhan.tran
    :date: 20-05-2024
    :param phone:
    :return: str
    """
    reg = r"^\+?1?\d{9,15}$"
    if not match(reg, phone):
        raise ValueError("Invalid phone number")
    return phone


def validate_password(password) -> str:
    """
    Validate password
    :author: nhan.tran
    :date: 20-05-2024
    :param password:
    :return: str
    """
    re = (r"^(?=.*[0-9])(?=.*[A-Z])(?=.*[a-z])(?=.*[~`!@#$%^&*()--+={}[\]|\\:;\"'<>,.?/_₹])[a-zA-Z0-9~`!@#$%^&*()--+={"
          r"}[\]|\\:;\"'<>,.?/_₹]{7,}$")
    if not match(re, password):
        raise ValueError("Invalid password format")
    return password


def generate_pagination_response(data: list | type(None),
                                 total: int,
                                 page: int,
                                 limit: int,
                                 endpoint: str):
    next_page = f"{endpoint}?page={page + 1}&limit={limit}" \
        if len(data) < total - page * limit else None
    prev_page = f"{endpoint}?page={page - 1}&limit={limit}" \
        if page > 0 and total > 0 else None

    return PaginationResponse(
        data=data,
        next=next_page,
        prev=prev_page,
        total=total,
        page=page,
        limit=limit
    )


def generate_id(length: int = 8):
    random_bytes = secrets.token_bytes(length // 2)
    id_part_1 = "".join([f"{b:02x}" for b in random_bytes])
    id_part_2 = ''.join(random.choice(string.ascii_letters) for x in range(length - len(id_part_1)))
    return id_part_1 + id_part_2


def gzip_data(data: str) -> bytes:
    """
    Gzip data
    :author: nhan.tran
    :date: 16-07-2024
    :param data:
    :return: bytes
    """
    zipped_data = compress(data.encode("ascii"), compresslevel=9)
    b64_encoded_data = base64.b64encode(zipped_data)
    return b64_encoded_data
