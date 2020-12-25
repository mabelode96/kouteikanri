from django import template
import datetime

register = template.Library()


@register.filter(name="seisantime")
def seisantime(end, start):
    if end is None:
        return 0
    elif start is None:
        return 0
    else:
        td = end - start
        return int(td.seconds / 60)


@register.filter(name="comp_time")
def comp_time(end, left):
    if end is None:
        et = datetime.datetime.now().astimezone()
    else:
        et = end
    if left is None:
        lm = 0
    else:
        lm = left
    d = int(lm / 1440)
    h = int((lm - d * 1440) / 60)
    m = int((lm - d * 1440) - h * 60)
    s = ((lm - d * 1440) - h * 60) - m
    td = et + datetime.timedelta(days=d, hours=h, minutes=m, seconds=s)
    return td


@register.filter(name="str_to_date")
def str_to_date(date_str):
    d = datetime.datetime.strptime(date_str, "%Y年%m月%d日")
    return d.strftime("%Y-%m-%d")


@register.filter(name="date_to_str")
def date_to_str(date_str):
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return d.strftime("%Y年%#m月%#d日")


@register.filter(name="get_nouryoku")
def get_nouryoku(value, process):
    if value is not None:
        if process is not None:
            try:
                n = round(value / (process / 60))
                return n
            except ZeroDivisionError:
                return 0
        else:
            return 0
    else:
        return 0
