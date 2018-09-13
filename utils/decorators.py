
# $Id: decorators.py 297 2007-04-07 00:37:52Z suriya $

from django.conf import settings
from django.http import HttpResponseRedirect

def func_attrs(**kwds):
    """Set attributes for a function.

    Example usage
    @func_attrs(allow_tags=True, short_description='Hello World')
    def function(args):
        ...
    """
    def decorate(f):
        for k in kwds:
            setattr(f, k, kwds[k])
        return f
    return decorate

