
# $Id: urls.py 354 2007-05-20 17:03:20Z suriya $

from django.conf.urls.defaults import *
from vibha.projects.sitemap import ProjectsSitemap
from vibha.projects.models import Project

urlpatterns = patterns('',
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': {'projects': ProjectsSitemap}}),
)

# Using generic view for project listing. This allows us to use pagination easily.
urlpatterns += patterns('django.views.generic.list_detail',
  (r'^$', 'object_list', {'queryset': Project.current_projects.order_by('name'),
                          'paginate_by': 10,
                          'template_name': 'projects/listing.dmpl',
                          'template_object_name': 'project',
                          'extra_context': {'projects': 'current'},
                          'allow_empty': True, }),
)
urlpatterns += patterns('django.views.generic.list_detail',
  (r'^past$', 'object_list', {'queryset': Project.past_projects.order_by('name'),
                          'paginate_by': 10,
                          'template_name': 'projects/listing.dmpl',
                          'template_object_name': 'project',
                          'extra_context': {'projects': 'past'},
                          'allow_empty': True, }),
)

from vibha.projects.views import map, detail, factsheet, agreement, gallery, gallery_xml, contactlead, thanks_for_contacting_us
urlpatterns += patterns('',
    (r'^map/$',                 map),         # Vibha projects using the Google maps API
    (r'^([-\w]+)/contactlead/$', contactlead), # Contact project lead
    (r'^thanks_for_contacting_us/$', thanks_for_contacting_us), # Contact project lead
    (r'^([-\w]+)/$',            detail),      # Display one project page using the slug field
    (r'^([-\w]+)/factsheet/$',  factsheet),   # Display a project's factsheet using the slug field
    (r'^([-\w]+)/agreement/$',  agreement),   # Display a project's partnership agreement (PDF) using the slug field
    (r'^([-\w]+)/gallery/$',    gallery),     # Gallery
    (r'^([-\w]+)/galleryxml/$', gallery_xml), # XML file for gallery
)
