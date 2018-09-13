
# $Id: urls.py 378 2007-06-26 21:12:31Z suriya $

from django.conf.urls.defaults import *
from vibha.cfc.views import sfp
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    (r'^new/$',                           sfp.view),
    (r'^thanks/$',                        direct_to_template, {'template': 'cfc/thanks.html'}),
)
