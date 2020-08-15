from datetime import timedelta, datetime


def format_td(d: timedelta) -> str:
    t = int(d.total_seconds())

    if t < 60:
        return f"{t} seconds"

    t //= 60

    if t < 60:
        return f"{t} minutes"

    t //= 60

    if t < 24:
        return f"{t} hours"

    t //= 24

    if t < 365:
        return f"{t} days"

    return "over a year"


def format_diff(dt: datetime) -> str:
    return format_td(datetime.now() - dt)
