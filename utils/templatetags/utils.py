
# $Id: utils.py 408 2007-12-03 16:55:48Z suriya $

from django import template
from django.template.defaultfilters import linebreaksbr

register = template.Library()

@register.filter
def doslinebreaksbr(text):
    return linebreaksbr(text.replace('\r', ''))

@register.filter
def multiply(text, arg):
    try:
        return unicode(int(text) * int(arg))
    except ValueError:
        return u''

@register.filter
def add(text, arg):
    try:
        return unicode(int(text) + int(arg))
    except ValueError:
        return ''

@register.simple_tag
def apply(func, o):
    """Apply function on object."""
    try:
        return unicode(func(o))
    except:
        return u'Not parsable'

from os.path import basename
register.filter('basename', basename)
