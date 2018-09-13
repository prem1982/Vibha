
# $Id: urls.py 434 2008-01-28 01:33:39Z suriya $

from django.conf.urls.defaults import *
from vibha.dream.views import sfp, index, event

urlpatterns = patterns('',
#   (r'^new/$',                           sfp.view), # Vibha projects using the Google maps API
#   (r"^events/$",                  index),    # Display a list of all events
    (r"^events/(?P<slug>[-\w]+)/$", event),    # Display an event usign the slug field
)
