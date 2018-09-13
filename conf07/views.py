# $Id: views.py 436 2008-02-03 20:47:11Z suriya $

# Create your views here.

from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from vibha.utils import newforms as vibhaforms
from django.core.mail import send_mail
from vibha.conf07.models import Signup
from vibha.utils.newforms.simpleformprocessing import SimpleFormProcessing
 
class SignupForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

    first_name     = vibhaforms.CharField(max_length=100)
    last_name      = vibhaforms.CharField(max_length=100)
    ac             = vibhaforms.CharField(label='Action Center or Location',
                     max_length=100)
    email          = vibhaforms.EmailField()
    webcast        = forms.BooleanField(
                        label='Viewing webcast?', 
                     help_text="""Are you following the conference through 
                     the webcast? """, initial=True, required=False)
    accomodation   = forms.BooleanField(label='Accomodation', 
                     help_text="""Check the box to request accomodation with 
                     a Vibha volunteer""", required=False)
    guests         = vibhaforms.CharField(label='Additional guests', 
                     help_text="""If you have additional guests traveling 
                     with you, enter their names""", required=False, 
                     widget=forms.Textarea(attrs={'rows': 5}))
    pickup         = forms.BooleanField(label='Airport pickup', 
                     help_text="""Check the box if you need a ride from the 
                     airport""", required=False)
    transportation = forms.BooleanField(label='Transportation', 
                     help_text="""Check the box if you need a ride to and 
                     from the conference venue""", required=False)
    requests       = vibhaforms.CharField(label='Other requests', 
                     required=False, widget=forms.Textarea(attrs={'rows': 5}))
    volunteer      = forms.BooleanField(label='Interested in Volunteering?', 
                     help_text="""If you check this box, you may be called 
                     upon to help out with tasks at the conference venue""", 
                     required=False)

def signupform_2_model(form):
    if not form.is_valid():
        return None
    data = form.cleaned_data
    signup = Signup(first_name=data['first_name'], last_name=data['last_name'],
                    ac=data['ac'], email=data['email'], 
                    webcast_viewing=data['webcast'],
                    accomodation=data['accomodation'],
                    guests=data['guests'], pickup=data['pickup'],
                    transportation=data['transportation'], 
                    requests=data['requests'], volunteer=data['volunteer'])
    signup.save()
    return signup

sfp = SimpleFormProcessing(
        form_class=SignupForm,
        form_2_model=signupform_2_model,
        form_template='conf07/create_signup_form.dmpl',
        email_template='conf07/response_email.dmpl',
        email_subject="Vibha Volunteer Conference Minnesota 2010 Signup",
        email_sender='volunteer@vibha.org',
        redirect_url='/conf/thanks/',
        do_captcha=True)

# vim:tw=150:nowrap:ts=4:sw=4:et:
