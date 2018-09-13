
# $Id: singledonation.py 431 2008-01-27 21:53:30Z suriya $

# Create your views here.

from vibha.utils.shortcuts import states_in_the_US_and_other, vibha_action_centers, is_in_US, get_object_or_none
from django.shortcuts import get_object_or_404
from django import forms
from vibha.utils import newforms as vibhaforms
from django.contrib.localflavor.us.forms import USZipCodeField, USPhoneNumberField
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from vibha.utils.creditcard import transact
from vibha.donations.models import Donation, Company
import decimal
from vibha.utils.newforms.complexformprocessing import ComplexFormProcessing
from datetime import date
import logging
from vibha.dream.models import Event
from vibha.austinchampion.models import Champion
from vibha.projects.models import Project
import re

TODAY = date.today()

# Keys for session data
PREFIX = 'vibha.donations.views.singledonation.'
DONATION_DATA = PREFIX + 'donation'

###########################################################
# The form for a donation.
# Contains validation logic.
###########################################################

def generate_form_class(text_field_size):
    """
    A form class with customizable sizes of text fields.  This is so ugly.
    Don't know any other way to do this.
    """
    class DonationForm(forms.Form):

        def __init__(self, *args, **kwargs):
            super(DonationForm, self).__init__(*args, **kwargs)
            self.fields['state']._fill_choices(states_in_the_US_and_other())
            self.fields['action_center']._fill_choices(vibha_action_centers())

        # Contact information
        email      = vibhaforms.EmailField(help_text='Official receipts will be emailed to this address', widget=forms.TextInput(attrs={'size': text_field_size}))
        first_name = vibhaforms.CharField(max_length=100, widget=forms.TextInput(attrs={'size': text_field_size}))
        last_name = vibhaforms.CharField(max_length=100, widget=forms.TextInput(attrs={'size': text_field_size}))
        address_1 = vibhaforms.CharField(label='Address', max_length=100, widget=forms.TextInput(attrs={'size': text_field_size}))
        address_2 = vibhaforms.CharField(label='Address (line 2)', required=False, max_length=100, widget=forms.TextInput(attrs={'size': text_field_size}))
        city      = vibhaforms.CharField(max_length=100, widget=forms.TextInput(attrs={'size': text_field_size}))
        state     = vibhaforms.ForeignKeyChoiceField(help_text='Please use "Other" listed at the end for a non-US address')
        zipcode   = vibhaforms.CharField(max_length=100, widget=forms.TextInput(attrs={'size': text_field_size}))
        country   = vibhaforms.CharField(max_length=100, initial='United States', widget=forms.TextInput(attrs={'size': text_field_size}))
        action_center = vibhaforms.ForeignKeyChoiceField(required=False, help_text='Vibha action center geographically closest to your area')
        phone     = USPhoneNumberField(help_text='Eg: 111-111-1111')

        # Amount
        AMOUNT_CHOICES = [
            ('20.00', "$20"),
            ('50.00', "$50"),
            ('120.00', "$120"),
            ('420.00', "$420"),
            ('900.00', "$900"),
            ('0',      "Other"),
        ]
        amount_choice = forms.ChoiceField(choices=AMOUNT_CHOICES, initial='0', widget=vibhaforms.RadioSelect(show_br=False))
        amount = forms.DecimalField(max_digits=9, decimal_places=2, min_value=decimal.Decimal("1.00"), help_text='Amount in dollars and cents (E.g. 50.00)')

        # credit card information
        cc_name     = vibhaforms.CharField(label='Name', max_length=100, help_text='Full name as it appears on the credit card', widget=forms.TextInput(attrs={'size': text_field_size}))
        credit_card = vibhaforms.CreditCardField(label='Card Number',
                widget=forms.TextInput(attrs={'autocomplete': 'off'}),
                help_text=u"""The address on the credit card must match the
                address above. We accept Visa, Mastercard, American Express,
                Discover.""")
        expr_date   = vibhaforms.MonthYearField(label='Expiry date')
        cvv         = vibhaforms.CharField(max_length=4, label='Security Code',
                widget=forms.TextInput(attrs={'autocomplete': 'off', 'size': 5}),
                help_text=u"""Three-digit credit card security code on the back
                for your Visa/Mastercard/Discover card or the four-digit code
                on the front of your American Express card. This code helps
                prevent frauds. <a
                href="javascript:popUp('http://www.merchantamerica.com/help.php?id=23#guide')">Need
                Help?</a>""")

        # Matching donation
        company_name = vibhaforms.CharField(label='Company',
                required=False, max_length=256, widget=forms.TextInput(attrs={'size': text_field_size}))
        company_id   = forms.IntegerField(required=False, widget=forms.HiddenInput())

        # Which dream registry event?
        dream_event_id   = forms.IntegerField(required=False, widget=forms.HiddenInput())

        # Comment
        comments     = vibhaforms.CharField(label='Other Comments', required=False, widget=forms.Textarea(attrs={'rows': 5}))

        # Email subscription information
        event_subscription = forms.BooleanField(required=False, initial=True)
        project_subscription = forms.BooleanField(required=False, initial=True)
        paper_receipt = forms.BooleanField(required=False, initial=False)

        # Which Austin champion caused this donation?
        champion_id      = forms.IntegerField(required=False, widget=forms.HiddenInput())

        # Which project is this donation made out to?
        project_id       = forms.IntegerField(required=False, widget=forms.HiddenInput())


        anonymous        = forms.BooleanField(label='Remain anonymous',
                initial=False, required=False, help_text=u'Make my donation anonynous')

        # Comment
        comments     = vibhaforms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}))

        # Referral
        referrer     = vibhaforms.CharField(required=False, label=u'Honoree', help_text=u'Name of the person (if any) who referred you to make this donation')

        def clean_expr_date(self):
            clean_date = self.cleaned_data['expr_date']
            # Expr date needs to be cleaned only when credit card is used.
            if True:
                month, year = clean_date
                month, year = int(month), int(year)
                expr_date_in_future = ((year > TODAY.year) or ((year == TODAY.year) and (month >= TODAY.month)))
                if not expr_date_in_future:
                    raise forms.ValidationError(u'Expiry date is in the past.')
            return clean_date

        def clean_amount_choice(self):
            ac = self.cleaned_data['amount_choice']
            self.fields['amount'].required = (ac == '0')
            return ac

        def clean_zipcode(self):
            state = self.cleaned_data.get('state', None)
            zipcode = self.cleaned_data['zipcode']
            if ((state is not None) and
                (zipcode is not None) and
                is_in_US(state) and
                (not re.match(r'^\d{5}(?:-\d{4})?$', zipcode))):
                raise forms.ValidationError(u'Enter a zip code in the format XXXXX or XXXXX-XXXX.')
            else:
                return zipcode

        def clean(self):
            # Handle amount choice
            self.fields['amount'].required = True
            ac = self.cleaned_data.get('amount_choice', '0')
            if ac != '0':
                self.cleaned_data['amount'] = decimal.Decimal(ac)
            return self.cleaned_data
    return DonationForm

#######################################################################################
# Process the credit card transaction.
#######################################################################################

def process_transaction(cleaned_data):
    """
    donation_info: a dictionary containing donation information

    Create a Donation row in the database, and talk to the payment gateway,
    and return a status message.
    """
    # Write donation details to the database
    credit_card = cleaned_data['credit_card']
    expr_month, expr_year = cleaned_data['expr_date']
    cnp_security = cleaned_data['cvv']
    amount = cleaned_data['amount']
    address_1 = cleaned_data['address_1']
    zipcode = cleaned_data['zipcode']
    ip_address = cleaned_data['ip_address']
    company = get_object_or_none(Company, id=cleaned_data['company_id'])
    dream_event = get_object_or_none(Event, id=cleaned_data['dream_event_id'])
    champion = get_object_or_none(Champion, id=cleaned_data['champion_id'])
    project = get_object_or_none(Project, id=cleaned_data['project_id'])
    d = Donation(
        first_name=cleaned_data['first_name'],
        last_name=cleaned_data['last_name'],
        email=cleaned_data['email'],
        address_1=address_1,
        address_2=cleaned_data['address_2'],
        city=cleaned_data['city'],
        state=cleaned_data['state'],
        action_center=cleaned_data['action_center'],
        zipcode=zipcode,
        country=cleaned_data['country'],
        phone=cleaned_data['phone'],
        amount=amount,
        ip_address=ip_address,
        comments=cleaned_data['comments'],
        referrer=cleaned_data['referrer'],
        company=company,
        company_name=cleaned_data['company_name'],
        dream_event=dream_event,
        paper_receipt=cleaned_data['paper_receipt'],
        project_subscription=cleaned_data['project_subscription'],
        event_subscription=cleaned_data['event_subscription'],
        champion=champion,
        project=project,
        anonymous=cleaned_data['anonymous'])
    d.save()
    # Process the transaction
    logging.info('process_transaction: expr_month: %s, expr_year: %s', expr_month, expr_year)
    if project is not None:
        logging.info('process_transaction: project specific donation to: %s', unicode(project))
    (trans_status, trans_summary, trans_response) = transact(credit_card,
            expr_month, expr_year, cnp_security, amount, address_1, zipcode, ip_address)
    # Write transaction information to the database
    d.trans_status = trans_status
    d.trans_summary = trans_summary
    d.trans_response = trans_response
    d.save()
    # Send e-mail to concered people in Vibha, if a transaction fails.
    if not trans_status:
        recipients = [ 'amenon81@gmail.com', 'ramdas@gmail.com' ]
        body = render_to_string('donations/singledonation-error-email.txt', {'model': d})
        email = EmailMessage('Error while processing single donation, please take a look', body, 'donations@vibha.org', recipients)
        email.attach('response.html', d.trans_response, 'text/html')
        email.send(fail_silently=False)
    return d

def model_2_redirect_url(model):
    if model.trans_status:
        return '/donations/single/thanks/'
    else:
        return '/donations/single/error/'

def dreammile_model_2_redirect_url(model):
    if model.trans_status:
        return '/dreammile/austin/thanks/'
    else:
        return '/dreammile/austin/error/'

def model_2_should_send_email(model):
    return model.trans_status

cfp = ComplexFormProcessing(
        form_session_name=DONATION_DATA,
        form_class=generate_form_class(35),
        cleaned_data_2_model=process_transaction,
        form_template='donations/singledonation-form.html',
        confirm_template='donations/singledonation-confirmdetails.html',
        model_2_should_send_email=model_2_should_send_email,
        email_template='donations/singledonation-email.txt',
        email_html_template='donations/singledonation-email.html',
        email_subject='Thank you for donating to Vibha',
        email_sender='donations@vibha.org',
        model_2_redirect_url=model_2_redirect_url,
        do_captcha=True,
        record_ip_addr=True)

dream_cfp = ComplexFormProcessing(
        form_session_name=DONATION_DATA,
        form_class=generate_form_class(35),
        cleaned_data_2_model=process_transaction,
        form_template='donations/dream-singledonation-form.html',
        confirm_template='donations/dream-singledonation-confirmdetails.html',
        model_2_should_send_email=model_2_should_send_email,
        email_template='donations/dream-singledonation-email.txt',
        email_html_template='donations/dream-singledonation-email.html',
        email_subject='Thank you for donating to Vibha',
        email_sender='donations@vibha.org',
        model_2_redirect_url=model_2_redirect_url,
        do_captcha=True,
        record_ip_addr=True)

def dream_registry_donation(request, slug):
    dream_event = get_object_or_404(Event, slug=slug)
    initial = { 'dream_event_id': dream_event.id }
    return dream_cfp.view(request, initial=initial, extra_form_template_args={'dream_event': dream_event})

dreammile_cfp = ComplexFormProcessing(
        form_session_name=DONATION_DATA,
        form_class=generate_form_class(25),
        cleaned_data_2_model=process_transaction,
        form_template='donations/dreammile/form.html',
        confirm_template='donations/dreammile/confirmdetails.html',
        model_2_should_send_email=model_2_should_send_email,
        email_template='donations/dreammile/email.txt',
        email_subject='Thank you for donating to Vibha',
        email_sender='donations@vibha.org',
        model_2_redirect_url=dreammile_model_2_redirect_url,
        do_captcha=True,
        record_ip_addr=True)

def dreammile_donation(request, slug):
    champion = get_object_or_404(Champion, slug=slug)
    initial = { 'champion_id': champion.id }
    return dreammile_cfp.view(request, initial=initial, extra_form_template_args={'champion': champion})

project_specific_cfp = ComplexFormProcessing(
        form_session_name=DONATION_DATA,
        form_class=generate_form_class(35),
        cleaned_data_2_model=process_transaction,
        form_template='donations/project-specific/form.html',
        confirm_template='donations/project-specific/confirmdetails.html',
        model_2_should_send_email=model_2_should_send_email,
        email_template='donations/project-specific/email.txt',
        email_subject='Thank you for donating to Vibha',
        email_sender='donations@vibha.org',
        model_2_redirect_url=model_2_redirect_url,
        do_captcha=True,
        record_ip_addr=True)

def project_specific_donation(request, slug):
    project = get_object_or_404(Project, slug=slug)
    initial = { 'project_id': project.id }
    return project_specific_cfp.view(request, initial=initial, extra_form_template_args={'project': project})

# vim:nowrap:ts=4:sw=4:et:
