from datetime import timedelta, datetime
from django import template

register = template.Library()


@register.filter(name="td2str")
def format_td(d: timedelta) -> str:
    t = int(d.total_seconds())

    if t < 60:
        return f"{t} s"

    t //= 60

    if t < 60:
        return f"{t} m"

    t //= 60

    if t < 24:
        return f"{t} h"

    t //= 24

    if t < 365:
        return f"{t} d"

    return ">1 y"


@register.filter(name="diff2str")
def format_diff(dt: datetime) -> str:
    return format_td(datetime.now() - dt)


@register.filter(name="client_style_cls")
def client_style_cls(client) -> str:
    if client["output_muted"]:
        return "output-muted"

    if client["input_muted"]:
        return "input-muted"

    if client["talking"]:
        return "talking"

    return ""


@register.filter(name="channel_style_cls")
def channel_style_cls(channel):
    return ""