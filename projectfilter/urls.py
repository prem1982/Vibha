from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('vibha.projectfilter.views',
    url(r'^list/$','filter_projects',name="list_projects"),
    url(r'^([-\w]+)/$','project_page',name="project_page"),
    url(r'^([-\w]+)/tell-friend/$','tell_friend',name="tell_friend"),
)
