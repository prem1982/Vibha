from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list

from django.contrib.auth.models import User

urlpatterns = patterns('vibha.donorportal.views',
    url(r'^projects/$','portal_projects',name='portal_home'),
    url(r'^cart/$','portal_cart',name='portal_cart'),
    url(r'^cart/delete/(?P<cart_element_id>\d+)/$','delete_cart_element',name='portal_cart_delete'),
    url(r'^cart/submit/$','cart_submit', name='portal_cart_submit'),
    url(r'^cart/checkout/$','cart_checkout', name='portal_cart_checkout'),
    url(r'^projects/$','portal_projects',name='portal_projects'),
    url(r'^campaign/(?P<campaign_id>\d+)/$','campaign',name='portal_campaign'),
    url(r'^campaign/$','campaign_list',name='portal_campaign_list'),
    url(r'^create-campaign/$','create_campaign_message',name='portal_create_campaign_start'),
    #url(r'^create-campaign-donate/$','create_campaign_donate',name='portal_create_campaign_donate'),
    #url(r'^create-campaign-message/$','create_campaign_message',name='portal_create_campaign_message'),
    #url(r'^create-campaign-page/$','create_campaign_page',name='portal_create_campaign_page'),
    url(r'^pp/$','debug'),
    url(r'^donations/$','portal_donations',name='portal_donations'),
    url(r'^donations/dup_receipt/$','duplicate_receipt',name='portal_donations_receipt'),
    url(r'^campaigns/$','portal_campaigns',name='portal_campaigns'),
    url(r'^watch/$',
        'portal_watch',
        name='portal_watch'),
    url(r'^watch/(?P<project_slug>[-\w]+)/$',
        'watch_project_toggle',
        name='portal_watch_project_toggle')
)
