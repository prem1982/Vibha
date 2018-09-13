
# $Id: captcha.py 315 2007-04-19 19:49:23Z suriya $

from django import template

register = template.Library()

@register.inclusion_tag('utils/captcha_field.html')
def captcha_field(form):
    return {'form': form}
