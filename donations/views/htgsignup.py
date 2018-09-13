
# $Id: htgsignup.py 422 2007-12-31 02:20:12Z suriya $

# Create your views here.

import decimal
from vibha.utils.shortcuts import states_in_the_US_and_other, vibha_action_centers, is_in_US, get_object_or_none
from django import forms
from vibha.utils import newforms as vibhaforms
from django.contrib.localflavor.us.forms import USZipCodeField, USPhoneNumberField
from vibha.donations.models import HTGSignup, Company
from vibha.utils.newforms.simpleformprocessing import SimpleFormProcessing
from datetime import date

TODAY = date.today()

class HTGSignupForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(HTGSignupForm, self).__init__(*args, **kwargs)
        self.fields['state']._fill_choices(states_in_the_US_and_other())

    # Contact information
    email      = vibhaforms.EmailField()
    first_name = vibhaforms.CharField(max_length=100, widget=forms.TextInput(attrs={'size': 35}))
    last_name = vibhaforms.CharField(max_length=100)
    address_1 = vibhaforms.CharField(label='Address', max_length=100)
    address_2 = vibhaforms.CharField(label='Address (line 2)', required=False, max_length=100)
    city      = vibhaforms.CharField(max_length=100)
    state     = vibhaforms.ForeignKeyChoiceField(help_text='Please use "Other" listed at the end for a non-US address')
    zipcode   = vibhaforms.CharField(max_length=100)
    country   = vibhaforms.CharField(max_length=100, initial='United States')
    phone     = vibhaforms.CharField(required=False, help_text='Eg: 111-111-1111')

    # Amount
    AMOUNT_CHOICES = [
        ('100.00', "$100 (funds a teacher's salary)"),
        ('75.00',  "$75  (funds a non-formal education center attended by 25 children)"),
        ('30.00',  "$30  (funds education and health care for a mentally challenged child)"),
        ('20.00',  "$20  (funds the education, health care and shelter for a child)"),
        ('0',      "Other"),
    ]
    amount_choice = forms.ChoiceField(choices=AMOUNT_CHOICES, widget=vibhaforms.RadioSelect(show_br=True))
    amount = forms.DecimalField(max_digits=9, decimal_places=2, min_value=decimal.Decimal("1.00"), help_text='Amount in dollars and cents (E.g. 50.00)')

    # bank or credit card
    # This field should be declared before the cc, and cheque fields given
    # below.
    USE_CC_CHOICE = [
        (u'Card',  u'Credit Card'),
        (u'Check', u'Bank Account'),
    ]
    use_cc = forms.ChoiceField(choices=USE_CC_CHOICE,
            label=u'Payment option',
            initial=u'Card',
            help_text='Do you want to use a credit card or check from a bank account?',
            widget=vibhaforms.RadioSelect(show_br=False))

    # credit card information
    cc_name     = vibhaforms.CharField(label='Name', max_length=100, help_text='Full name as it appears on the credit card')
    credit_card = vibhaforms.CreditCardField(help_text='Eg: 4111111111111111.  The address on the credit card must match the address above.')
    expr_date   = vibhaforms.MonthYearField(label='Expiry date')
#     cvv         = forms.CharField(max_length=4, help_text='Credit card authorization number')

    # bank account information
    bank_name   = vibhaforms.CharField(max_length=100)
    aba_number  = vibhaforms.ABANumberField(label=u"Routing Number",
            help_text="""<a target="_blank" href="https://www.merchantamerica.com/help/adm_help_routing_number.html">What's this?</a>""")
    account_number = vibhaforms.CharField(max_length=100)

    # Matching donation
    company_name = vibhaforms.CharField(label='Company', required=False, max_length=256)
    company_id   = forms.IntegerField(required=False, widget=forms.HiddenInput())

    paper_receipt        = forms.BooleanField(required=False, initial=False)
    project_subscription = forms.BooleanField(required=False, initial=True)
    event_subscription   = forms.BooleanField(required=False, initial=True)
    referrer             = vibhaforms.CharField(required=False, label=u'Honoree', 
            help_text=u'Name of the person (if any) who referred you to make this donation')
    comments             = vibhaforms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}))


    def clean_use_cc(self):
        """
        If use_cc is selected, ignore the cheque fields, and vice versa
        """
        u = self.cleaned_data['use_cc']
        if u == u'Card':
            self.fields['cc_name'].required = self.fields['credit_card'].required = self.fields['expr_date'].required = True
            self.fields['bank_name'].required = self.fields['aba_number'].required = self.fields['account_number'].required = False
            # del self.data['bank_name']; del self.data['aba_number']; del self.fields['account_number']
            return True
        else:
            self.fields['cc_name'].required = self.fields['credit_card'].required = self.fields['expr_date'].required = False
            self.fields['bank_name'].required = self.fields['aba_number'].required = self.fields['account_number'].required = True
            # del self.data['cc_name']; del self.data['credit_card']; del self.fields['expr_date']
            return False

    def clean_expr_date(self):
        clean_date = self.cleaned_data['expr_date']
        # Expr date needs to be cleaned only when credit card is used.
        if self.cleaned_data['use_cc'] == True:
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

    def clean(self):
        self.fields['cc_name'].required = self.fields['credit_card'].required = self.fields['expr_date'].required = True
        self.fields['bank_name'].required = self.fields['aba_number'].required = self.fields['account_number'].required = True
        self.fields['amount'].required = True
        ac = self.cleaned_data.get('amount_choice', '0')
        if ac != '0':
            self.cleaned_data['amount'] = decimal.Decimal(ac)
        return self.cleaned_data

def form_2_model(form):
    """
    Convert the HTGSignupForm above to HTGSignup model
    """
    d = form.cleaned_data
    use_cc = d['use_cc']
    if use_cc:
        expr_month, expr_year = d['expr_date']
    else:
        expr_month, expr_year = None, None
    company = get_object_or_none(Company, id=d['company_id'])
    newsignup = HTGSignup(first_name=d['first_name'],
              last_name=d['last_name'],
              email=d['email'],
              address_1=d['address_1'],
              address_2=d['address_2'],
              city=d['city'],
              state=d['state'],
              zipcode=d['zipcode'],
              country=d['country'],
              phone=d['phone'],
              amount=d['amount'],
              use_check=not use_cc,
              bank_name=d.get('bank_name'),
              aba_number=d.get('aba_number'),
              account_number=d.get('account_number'),
              cc_ac_name=d.get('cc_name'),
              cc_number=d.get('credit_card'),
              cc_expr_month=expr_month,
              cc_expr_year=expr_year,
              company=company,
              company_name=d['company_name'],
              ip_address=d['ip_address'],
              paper_receipt=d['paper_receipt'],
              project_subscription=d['project_subscription'],
              event_subscription=d['event_subscription'],
              referrer=d['referrer'],
              comments=d['comments']
              )
    newsignup.save()
    return newsignup

sfp = SimpleFormProcessing(
        form_class=HTGSignupForm,
        form_2_model=form_2_model,
        form_template='donations/htgsignup-form.html',
        email_template='donations/htgsignup-email.txt',
        email_subject='Vibha Help Them Grow Automatic Donation Program',
        email_sender='htg@vibha.org',
        redirect_url='/donations/htg/thanks/',
        do_captcha=True,
        record_ip_addr=True)

# vim:nowrap:ts=4:sw=4:et:
