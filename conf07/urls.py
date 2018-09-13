
# $Id: urls.py 436 2008-02-03 20:47:11Z suriya $

from django.conf.urls.defaults import *
from vibha.conf07.views import sfp

urlpatterns = patterns('',
    (r'^signup/$',                           sfp.view), # signup page
)
