
# $Id: urls.py 449 2008-04-02 20:46:49Z suriya $

from django.conf.urls.defaults import *
from vibha.triviaguru.views import sfp, redirect_to_paypal

urlpatterns = patterns('',
   (r'^register/$',  sfp.view),   # New registration
   (r'^pay/(\d+)/$', redirect_to_paypal),
)
