# $Id: projects_extras.py 293 2007-03-29 03:21:18Z suriya $

from django import template

register = template.Library()

@register.filter
def typewriter(s):
    return '&nbsp; <u> <b> <font name="courier"> %s </font> </b> &nbsp; </u>' % s
