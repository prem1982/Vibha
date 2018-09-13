# $Id: urls.py 445 2008-03-06 22:26:54Z suriya $

import os

from django.conf.urls.defaults import *
from vibha.projects.sitemap import ProjectsSitemap
from vibha.projects.models import Project
from vibha.projects.views import LatestReports

from django.contrib import admin
admin.autodiscover()

from django.views.generic.simple import direct_to_template
from vibha.donorportal.forms import AkismetInitContactForm
from vibha.contact_form.views import contact_form
from django.contrib.auth.decorators import login_required

handler404 = 'vibha.utils.views.page_not_found'

feeds = {
    'project-reports': LatestReports,
}

urlpatterns = patterns('',
    # Password changing stuff
    (r'^admin/password_reset/$',       'django.contrib.auth.views.password_reset'),
    (r'^admin/password_reset/done/$',  'django.contrib.auth.views.password_reset_done'),
    (r'^feeds/(?P<url>.*)/$',          'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    # Admin
    (r'^admin/(.*)', admin.site.root),
    # Projects stuff
    (r'^projects/',  include('vibha.projects.urls')),
    # Vibha Dream Registry
    (r'^dream/',     include('vibha.dream.urls')),
    # Volunteer Signups
    (r'^signups/',     include('vibha.signups.urls')),
    # Donations
    (r'^donations/', include('vibha.donations.urls')),
    # Change For Children
    (r'^cfc/',       include('vibha.cfc.urls')),
    # Volunteer Conference Signup
    (r'^conf/',    include('vibha.conf07.urls')),
    # Utils
    (r'^utils/',     include('vibha.utils.urls')),
    # Austin cricket tournament 2008
    (r'^austincricket/',    include('vibha.austincricket08.urls')),
    (r'^triviaguru/',         include('vibha.triviaguru.urls')),
    # Austin Vibha champion page
    (r'^dreammile/austin/', include('vibha.donations.austinchampionurls')),

    # Portal
    (r'^portal/',     include('vibha.donorportal.urls')),
    # Projects filter
    (r'^projectfilter/',     include('vibha.projectfilter.urls')),
    # Registration
    (r'^accounts/',include('vibha.registration.urls')),
    # Home page
    url(r'^home/$', 'vibha.projectfilter.views.home',name="homepage"),

    # Static pages
    url(r'^getinvolved/$', direct_to_template, {'template': 'getinvolved.dmpl', 'extra_context': {'active_link': 2}}),
    url(r'^about-us/$', direct_to_template, {'template': 'aboutus.dmpl', 'extra_context': {'active_link': 3}}),
    url(r'^aboutaap/$', direct_to_template, {'template': 'aboutaap.dmpl', 'extra_context': {'active_link': 4}}),
    
    (r'^profiles/', include('vibha.profiles.urls')),
    
    url(r'^contact/$',
        login_required(contact_form),
        {'form_class':AkismetInitContactForm},
        name='contact_form'),

    url(r'^contact/sent/$',
        direct_to_template,
        { 'template': 'contact_form/contact_form_sent.html' },
        name='contact_form_sent'),

    #For rendering dynamic admin js, used in calendar, for group_manager
    (r'^my_admin/jsi18n', 'django.views.i18n.javascript_catalog'),
    
    url(r"^search/$",
        'vibha.projectfilter.views.search',
        name="search")
)

# Thank the person for signing in
urlpatterns += patterns('django.views.generic.simple',
    (r"^signups/thanks/$",         'direct_to_template', {'template': 'signups/thanks.dmpl'}),
    (r"^dream/thanks/$",           'direct_to_template', {'template': 'dream/thanks.dmpl'}),
    (r"^conf/thanks/$",          'direct_to_template', {'template': 'conf07/thanks.dmpl'}),
    (r"^austincricket/thanks/$", 'direct_to_template', {'template': 'austincricket08/signup-thanks.html'}),
    (r"^triviaguru/thanks/$",      'direct_to_template', {'template': 'triviaguru/signup-thanks.html'}),
)

urlpatterns += patterns('vibha.donations.views',
    (r"^ajax/companies/$",      "matching.ajax_companies_list_response"), # List of companies for autocomplete
)

from django.conf import settings
if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'^vibha-media/(?P<path>.*)$', 'serve', { 'document_root': os.path.join(settings.VIBHA_DJANGO_ROOT, 'media') }),
        (r'^project-uploads/(?P<path>.*)$', 'serve', { 'document_root': settings.MEDIA_ROOT }),
    )
