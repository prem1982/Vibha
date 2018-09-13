from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from vibha.registration.forms import RegistrationForm
from django.contrib.auth.models import User
from vibha.registration.models import UserProfile
from django.contrib.auth.views import login,logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.contrib.auth import REDIRECT_FIELD_NAME, login,authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import Site, RequestSite
from django.template import RequestContext
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from django.views.generic.list_detail import object_list

from vibha.debug import *

REGISTRATION_MAIL= {'subject':'Thank you for registering with Vibha',
                    'message-template': 'registration/registration-email.txt',
                    'from_email':'info@vibha.org',
                    'cc_list':['adopt@vibha.org']
                   }


def register(request):
    if request.user.is_authenticated():
        # They already have an account; don't let them register again
        return HttpResponseRedirect(reverse('portal_home'))

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = User()
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            pw1 = form.cleaned_data['password1']
            new_user.set_password(pw1)

            new_user.first_name = form.cleaned_data['firstname']
            new_user.last_name = form.cleaned_data['lastname']
            new_user.save()

            new_user_profile = UserProfile(user=new_user,
                                           country=form.cleaned_data['country'])
            new_user_profile.save()

            msg = render_to_string(REGISTRATION_MAIL['message-template'], {'user': new_user})
            send_mail(
                subject = REGISTRATION_MAIL['subject'],
                message = msg,
                from_email = REGISTRATION_MAIL['from_email'],
                recipient_list = [new_user.email] + REGISTRATION_MAIL['cc_list'],
                fail_silently=False,
            )

            user_auth = authenticate(username=new_user.username,password=pw1)
            login(request,user_auth)
            request.user.message_set.create(message='Registration successful! You are now logged in. Please complete your profile.')
            return redirect('profiles_edit_profile')

            #request.info='You have been successfully registered. Login now'
            #return render_to_response('registration/login.html',{'info':'registered'},RequestContext(request))
    else:
        form = RegistrationForm()
    return render_to_response('registration/portal-register.html',
                              {'form':form},
                              )

def my_login(request):
    """
    Monkey patching username field to have length 75, else 30 by default.
    This is necessary because emails can be longer than 30
    """
    AuthenticationForm.base_fields['username'].max_length = 75
    return login(request)
    
