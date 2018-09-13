# Create your views here.

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from django import forms
from django.core.mail import send_mail
from vibha.utils.newforms.simpleformprocessing import SimpleFormProcessing
from vibha.signups.models import Contact
from django.template.defaultfilters import yesno
from vibha.utils import newforms as vibhaforms

class VolunteerSignupForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(VolunteerSignupForm, self).__init__(*args, **kwargs)
        self.fields['location']._fill_choices()
        self.fields['age']._fill_choices()
        self.fields['occupation']._fill_choices()
        self.fields['intro_source']._fill_choices()

    # Contact information
    email      = forms.EmailField(max_length=100)
    phone = forms.CharField(max_length=100, help_text=u'Eg: 111-111-1111',
            required=True)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    location = vibhaforms.AnotherChoiceField(choices=Contact.LOCATION_CHOICES)
    other_location = forms.CharField(max_length=100, required=False, label=u"", help_text=u"<i>Please enter your location if you choose 'Other':</i>")
    new_ac = forms.BooleanField(required=False, label=u"")
    
    # Interests
    int_projects = forms.BooleanField(required=False)
    int_fundraise = forms.BooleanField(required=False)
    int_volunteer = forms.BooleanField(required=False)
    int_it = forms.BooleanField(required=False)
    int_programs = forms.BooleanField(required=False)
    int_marketing = forms.BooleanField(required=False)

    # Other Info
    age = vibhaforms.AnotherChoiceField(label='Age Group', choices=Contact.AGE_CHOICES, required=False)
    occupation = vibhaforms.AnotherChoiceField(choices=Contact.OCCUPATION_CHOICES, required=False)
    intro_source = vibhaforms.AnotherChoiceField(label='Referral', choices=Contact.INTRO_SOURCE_CHOICES, help_text=u"How did you hear about Vibha?", required=False)
    comments     = forms.CharField(label='Other Comments', required=False, widget=forms.Textarea(attrs={'rows': 5}))
    
def volunteersignupform_2_model(form):
    if not form.is_valid():
        return None
    data = form.cleaned_data
    signup = Contact(email=data['email'], phone=data['phone'], first_name=data['first_name'], last_name=data['last_name'], location=data['location'], other_location=data['other_location'], new_ac=data['new_ac'], int_volunteer=data['int_volunteer'], int_projects=data['int_projects'], int_fundraise=data['int_fundraise'], int_it=data['int_it'], int_programs=data['int_programs'], int_marketing=data['int_marketing'], age=data['age'], occupation=data['occupation'], intro_source=data['intro_source'], comments=data['comments'])
    signup.save()
    # The next line is needed for signup.get_location_display() function to
    # work
    signup = Contact.objects.get(id=signup.id)
    return signup

sfp = SimpleFormProcessing(
    form_class=VolunteerSignupForm,
    form_2_model=volunteersignupform_2_model,
    form_template='signups/create_contact_form.dmpl',
    email_template='signups/response_email.dmpl',
    email_html_template='signups/response_email_html.dmpl',
    email_subject='Vibha Volunteer Signup',
    email_sender='volunteer@vibha.org',
    redirect_url='/signups/thanks/',
    do_captcha=True)

# vim:nowrap:
