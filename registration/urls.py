from django.conf.urls.defaults import *

from django.contrib.auth import views as auth_views
from vibha.registration.forms import RegistrationWizard,RegistrationForm,ProfileForm

urlpatterns = patterns('vibha.registration.views',
        url(r'^login/$',auth_views.login, name="login_view"),
    url(r'^logout/$',auth_views.logout,
        {'template_name':'registration/logout.html'},
        name='logout_view'),
    url(r'^register/$','register',name='register_view'),
    url(r'^passreset/$',auth_views.password_reset,name='forgot_password1'),
    url(r'^passresetdone/$',auth_views.password_reset_done,name='forgot_password2'),
    url(r'^passresetconfirm/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)/$',auth_views.password_reset_confirm,name='forgot_password3'),
    url(r'^passresetcomplete/$',auth_views.password_reset_complete,name='forgot_password4'),
    
)
    #url(r'^home/$','',name='filter_projects'),
    
    
