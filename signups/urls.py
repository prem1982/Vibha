
# $Id: urls.py 434 2008-01-28 01:33:39Z suriya $

from django.conf.urls.defaults import *
from vibha.signups.views import sfp

urlpatterns = patterns('',
   (r'^new/$',                           sfp.view)
)
