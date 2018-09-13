
# $Id: urls.py 430 2008-01-27 02:19:22Z suriya $

from django.conf.urls.defaults import *
from vibha.donations.views.htgsignup import sfp
from vibha.donations.views.singledonation import cfp, dream_registry_donation, project_specific_donation
from vibha.donations.views import echo_response
from vibha.donations.views.matching import company_list

urlpatterns = patterns('',
    (r'^htg/new/$', sfp.view),   # New HTG signup
    (r'^single/new/$', cfp.view), # Handle a single donation
    (r'^single/new/dream/([-\w]+)/$', dream_registry_donation), # Handle a dream registry donation
    (r'^single/new/project/([-\w]+)/$', project_specific_donation), # Handle a project specific donation
    (r'^single/echo-response/(\d+)/$', echo_response),
    (r'^matching/$', company_list),
)

urlpatterns += patterns('django.views.generic.simple',
      (r"^htg/thanks/$",    'direct_to_template', {'template': 'donations/htgsignup-thanks.html'}),
      (r"^single/thanks/$",    'direct_to_template', {'template': 'donations/singledonation-thanks.html'}),
      (r"^single/thanks-other/$",    'direct_to_template', {'template': 'donations/singledonation-thanks-other.html'}),
   (r"^single/error/$",     'direct_to_template', {'template': 'donations/singledonation-error.html'}),
)
