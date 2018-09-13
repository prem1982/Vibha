
# $Id: views.py 407 2007-12-03 05:20:21Z suriya $

from vibha.utils.shortcuts import states_in_the_US, vibha_action_centers
from django import forms
from vibha.utils import newforms as vibhaforms
from vibha.cfc.models import CFCSignup
from vibha.utils.newforms.simpleformprocessing import SimpleFormProcessing
from django.contrib.localflavor.us.forms import USZipCodeField, USPhoneNumberField

########################################################
# Process a new signup
########################################################
class CFCSignupForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(CFCSignupForm, self).__init__(*args, **kwargs)
        self.fields['state']._fill_choices(states_in_the_US())
        self.fields['actioncenter']._fill_choices(vibha_action_centers())

    first_name     = forms.CharField(label="First Name", max_length=100)
    last_name      = forms.CharField(label="Last Name",  max_length=100)
    pg_first_name  = forms.CharField(label="Parent/Guardian First Name", max_length=100, required=False)
    pg_last_name   = forms.CharField(label="Parent/Guardian Last Name", max_length=100, required=False)
    email          = forms.EmailField(label="E-mail")
    phone          = USPhoneNumberField()
    address_1      = forms.CharField(label="Address Line1", max_length=100, required=False)
    address_2      = forms.CharField(label="Address Line2", max_length=100, required=False)
    city	       = forms.CharField(label="City", max_length=100, required=False)
    state          = vibhaforms.ForeignKeyChoiceField(required=False)
    actioncenter   = vibhaforms.ForeignKeyChoiceField(required=False)
    zipcode        = USZipCodeField(required=False)
    comments       = forms.CharField(label="Comments", widget=forms.Textarea(), required=False)
    receipt        = forms.BooleanField(label="Need receipt?", required=False,
                     help_text="""If the donation box is kept at a common
                     place like office cubicle or break room where anybody
                     can drop the change, that money is not tax
                     deductible""")
    agreement      = forms.BooleanField(label="Agreement",
                     help_text="""By selecting this option, I attest that I
                     am above 18 years of age or my parent/guardian has
                     approved signing up for this program""")

def cfcsignupform_2_model(form):
    if not form.is_valid():
        return None
    data = form.cleaned_data
    signup = CFCSignup(
            first_name=data['first_name'],
            last_name=data['last_name'],
            pg_first_name=data['pg_first_name'],
            pg_last_name=data['pg_last_name'],
            email=data['email'],
            phone=data['phone'],
            address_1=data['address_1'],
            address_2=data['address_2'],
            city=data['city'],
            state=data['state'],
            actioncenter=data['actioncenter'],
            zipcode=data['zipcode'],
            comments=data['comments'],
            receipt=data['receipt'],
            agreement=data['agreement'])
    signup.save()
    return signup

sfp = SimpleFormProcessing(
        form_class=CFCSignupForm,
        form_2_model=cfcsignupform_2_model,
        form_template='cfc/cfcsignup_form.html',
        email_template='cfc/response_email.txt',
        email_subject='Thank you from Vibha Change For Children',
        email_sender='cfc@vibha.org',
        redirect_url='/cfc/thanks/',
        do_captcha=True)

# vim:nowrap:ts=4:sw=4:et:
