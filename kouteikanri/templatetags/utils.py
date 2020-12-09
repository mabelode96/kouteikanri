from django import template

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
