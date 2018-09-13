
# $Id: creditcard.py 315 2007-04-19 19:49:23Z suriya $

from django import template

register = template.Library()

@register.filter
def last4(text):
    return u'************%s' % text[-4:]
