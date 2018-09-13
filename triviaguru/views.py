# Create your views here.

from vibha.triviaguru.models import TriviaGuruRegistration
from vibha.utils import newforms as vibhaforms
from django import forms
from django.contrib.localflavor.us.forms import USPhoneNumberField
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from vibha.utils.newforms.simpleformprocessing import SimpleFormProcessing

class TriviaGuruRegistrationForm(forms.Form):
    captain_name = vibhaforms.CharField(label="Team Captain", max_length=100)
    email        = vibhaforms.EmailField()
    phone        = USPhoneNumberField(help_text='Eg: 111-111-1111')
    member2_name = vibhaforms.CharField(label="Team member 2", max_length=100, required=False,
            help_text=r"Leave this blank if you are registering individually or do not have a full team")
    member3_name = vibhaforms.CharField(label="Team member 3", max_length=100, required=False,
            help_text=r"Leave this blank if you are registering individually or do not have a full team")
    team_name    = vibhaforms.CharField(max_length=100)
    num_students     = forms.IntegerField(required=True, initial=0)
    num_non_students = forms.IntegerField(required=True, initial=0)
    comments  = vibhaforms.CharField(label="How did you hear about us?/Other comments", required=False, widget=forms.Textarea(attrs={'rows': 5}))

def form_2_model(form):
    """
    Convert the TriviaGuruRegistrationForm above to TriviaGuruRegistration
    """
    d = form.cleaned_data
    newregistration = TriviaGuruRegistration(
        captain_name=d['captain_name'],
        captain_email=d['email'],
        captain_phone=d['phone'],
        team_name=d['team_name'],
        member2_name=d['member2_name'],
        member3_name=d['member3_name'],
        num_students=d['num_students'],
        num_non_students=d['num_non_students'],
        comments=d['comments'],
    )
    newregistration.save()
    return newregistration

sfp = SimpleFormProcessing(
        form_class=TriviaGuruRegistrationForm,
        form_2_model=form_2_model,
        form_template='triviaguru/signup-form.html',
        email_template='triviaguru/signup-email.txt',
        email_subject='Vibha Trivia Guru 2008',
        email_sender='info@austin.vibha.org',
        redirect_url='/triviaguru/thanks/',
        do_captcha=True,
        record_ip_addr=False)

def redirect_to_paypal(request, id):
    team = get_object_or_404(TriviaGuruRegistration, id=id)
    return HttpResponseRedirect(team.paypal_url())

# vim:nowrap:ts=4:sw=4:et:
