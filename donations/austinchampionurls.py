
from django.conf.urls.defaults import *
from vibha.donations.views.singledonation import dreammile_donation
from vibha.austinchampion.views import welcome, fundraiser

urlpatterns = patterns('django.views.generic.simple',
   (r"^thanks/$",    'direct_to_template', {'template': 'donations/dreammile/thanks.html'}),
   (r"^error/$",     'direct_to_template', {'template': 'donations/dreammile/error.html'}),
)

# Important this be below the URLs above
urlpatterns += patterns('',
    (r'^$',                welcome),            # Austin's welcome page
    (r'^([-\w]+)/donate/$', dreammile_donation), # Handle a vibha champion donation
    (r'^([-\w]+)/$',        fundraiser), # Handle a vibha champion donation
)
