import datetime


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
