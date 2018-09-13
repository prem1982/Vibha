
# $Id: urls.py 372 2007-06-19 18:10:17Z suriya $

from django.conf.urls.defaults import *

#######################################################################
# URLs of the form
# /spreadsheets/html/app_label/model_name/field_list_var/
# of
# /spreadsheets/html/app_label/model_name/
#######################################################################
from vibha.utils.spreadsheets import csv_view, html_view
urlpatterns = patterns('',
    (r"^spreadsheets/csv/(\w+)/(\w+)/$",        csv_view),  # Return a CSV  file for this model
   (r"^spreadsheets/html/(\w+)/(\w+)/$",        html_view), # Return a HTML file for this model
    (r"^spreadsheets/csv/(\w+)/(\w+)/(\w+)/$",  csv_view),  # Return a CSV  file for this model
   (r"^spreadsheets/html/(\w+)/(\w+)/(\w+)/$",  html_view), # Return a HTML file for this model
)

# Captcha
from vibha.utils.captcha import captcha_image
urlpatterns += patterns('',
    (r"^captcha/$", captcha_image),
)
