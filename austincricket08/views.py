# Create your views here.

from vibha.austincricket08.models import AustinCricket08Registration
from vibha.utils import newforms as vibhaforms
from django import forms
from django.contrib.localflavor.us.forms import USPhoneNumberField
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from vibha.utils.newforms.simpleformprocessing import SimpleFormProcessing

class AustinCricket08RegistrationForm(forms.Form):
    first_name = vibhaforms.CharField(max_length=100)
    last_name  = vibhaforms.CharField(max_length=100)
    email      = vibhaforms.EmailField()
    phone      = USPhoneNumberField(help_text='Eg: 111-111-1111')
    INDIVIDUAL_TEAM_CHOICE = [
        (u'Team', u'Team registration'),
        (u'Individual', u'Individual registration'),
    ]
    individual = forms.ChoiceField(choices=INDIVIDUAL_TEAM_CHOICE,
        label=u'Team/Individual',
        initial=u'Team',
        widget=vibhaforms.RadioSelect(show_br=False))
    team_name = vibhaforms.CharField(max_length=100, required=False)
    num_students     = forms.IntegerField(required=False, initial=0)
    num_non_students = forms.IntegerField(help_text="""In case of team
            registration, there should be a total of eight players.""", required=False, initial=0)
    comments  = vibhaforms.CharField(label="How did you hear about us?/Other comments", required=False, widget=forms.Textarea(attrs={'rows': 5}))

def form_2_model(form):
    """
    Convert the AustinCricket08RegistrationForm above to
    AustinCricket08Registration
    """
    d = form.cleaned_data
    if d['individual'] == u'Individual':
        individual = True
    else:
        individual = False
    newregistration = AustinCricket08Registration(
        captain_first_name=d['first_name'],
        captain_last_name=d['last_name'],
        captain_email=d['email'],
        captain_phone=d['phone'],
        individual=individual,
        team_name=d['team_name'],
        num_students=d['num_students'],
        num_non_students=d['num_non_students'],
        comments=d['comments'],
    )
    newregistration.save()
    return newregistration

sfp = SimpleFormProcessing(
        form_class=AustinCricket08RegistrationForm,
        form_2_model=form_2_model,
        form_template='austincricket08/signup-form.html',
        email_template='austincricket08/signup-email.txt',
        email_subject='Vibha Austin Cricket Tournament 2011',
        email_sender='cricket@austin.vibha.org',
        redirect_url='/austincricket/thanks/',
        do_captcha=True,
        record_ip_addr=False)

def redirect_to_paypal(request, id):
    team = get_object_or_404(AustinCricket08Registration, id=id)
    return HttpResponseRedirect(team.paypal_url())

# vim:nowrap:ts=4:sw=4:et:
