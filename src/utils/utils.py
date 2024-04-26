import datetime
from re import match

from .PaginationModel import PaginationResponse


def get_timedelta(value, unit):
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


def validate_email(email):
    reg = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$"
    if not match(reg, email):
        raise ValueError("Invalid email")
    return email


def validate_phone(phone):
    reg = r"^\+?1?\d{9,15}$"
    if not match(reg, phone):
        raise ValueError("Invalid phone number")
    return phone


def validate_password(password):
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
