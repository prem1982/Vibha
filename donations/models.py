
# $Id: models.py 430 2008-01-27 02:19:22Z suriya $

from django.db import models
from vibha.projects.models import State, ActionCenter, Project
from vibha.utils import dates as vibhautilsdates
from vibha.utils.crypto import encrypt
from vibha.utils.decorators import func_attrs
from django.template.defaultfilters import yesno
from vibha.dream.models import Event
from vibha.austinchampion.models import Champion
from vibha.donorportal.models import Donation as AdoptAProjectDonation

class Company(models.Model):
    name             = models.CharField("Company name",       blank=False,          max_length=255)
    is_active        = models.BooleanField("Is Active?",      default=True)
    address_1        = models.CharField("Address 1",          blank=True,           max_length=255)
    address_2        = models.CharField("Address 2",          blank=True,           max_length=255)
    city             = models.CharField("City",               blank=True,           max_length=255)
    state            = models.ForeignKey(State,               blank=True,           null=True)
    zipcode          = models.CharField("Zip Code",           blank=True,           max_length=20)
    url              = models.URLField("URL",                 blank=True,           verify_exists=False)
    vibha_id         = models.CharField("Vibha ID",           blank=True,           max_length=255,        help_text="Vibha's ID in the company database")
    # Co-ordinator details
    first_name_coord = models.CharField("First name (coord)", blank=True,           max_length=255,        help_text="First name of matching donation coordinator at the company")
    last_name_coord  = models.CharField("Last name (coord)",  blank=True,           max_length=255,        help_text="Last name  of matching donation coordinator at the company")
    title_coord      = models.CharField("Title (coord)",      blank=True,           max_length=255,        help_text="Title of matching donation coordinator at the company")
    phone            = models.CharField("Phone",              blank=True,           max_length=255)
    alt_phone        = models.CharField("Alternate Phone",    blank=True,           max_length=255)
    fax              = models.CharField("Fax",                blank=True,           max_length=255)
    email            = models.EmailField("E-mail",            blank=True)
    procedure        = models.TextField("Procedure",          blank=True,           help_text="Brief procedure of how to get donation matched")
    comments         = models.TextField("Comments",           blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'companies'

    def __unicode__(self):
        return self.name

class Donation(models.Model):
    signup_date    = models.DateTimeField("Signup date",  editable=False, auto_now=True)
    first_name     = models.CharField("First name",        max_length=100)
    last_name      = models.CharField("Last name",         max_length=100)
    email          = models.EmailField("E-mail")
    address_1      = models.CharField("Address 1",  max_length=100, blank=False)
    address_2      = models.CharField("Address 2",  max_length=100, blank=True)
    city           = models.CharField("City",       max_length=100, blank=False)
    state          = models.ForeignKey(State,       null=True,      blank=True)
    zipcode        = models.CharField("Zip code",   max_length=100, blank=False)
    country        = models.CharField("Country",    max_length=100, blank=False)
    action_center  = models.ForeignKey(ActionCenter, null=True,     blank=True)
    phone          = models.CharField("Phone",      max_length=100, blank=False)
    amount         = models.DecimalField("Amount",    max_digits=9, decimal_places=2)
    comments       = models.TextField("Comments",   blank=True)

    # Twenty20 referrer
    referrer       = models.CharField("Referrer",   max_length=255, blank=True)

    # Matching donations information
    company        = models.ForeignKey(Company,        blank=True, null=True)
    # company_name is valid only if (company is None)
    # company_name is used when the company does not already exist in the Company table
    company_name   = models.CharField("Company name",  blank=True, max_length=100)

    # The dream registry event this donation is realted to.
    dream_event    = models.ForeignKey(Event,          blank=True, null=True)

    # The austin champion this donation is related to
    champion       = models.ForeignKey(Champion,       blank=True, null=True)

    # The project this donation is related to
    project        = models.ForeignKey(Project,        blank=True, null=True)

    anonymous      = models.BooleanField("Anonymous?", default=False)

    # IP address
    ip_address     = models.IPAddressField("IP Address", blank=True)

    # related to the transaction
    trans_status   = models.BooleanField("Transaction status", default=False)
    trans_summary  = models.CharField("One line response from Echo", max_length=256, blank=True)
    trans_response = models.TextField("Complete transaction info from Echo", blank=True)

    # Subscription information
    project_subscription = models.BooleanField("Project Subscription", default=True)
    event_subscription = models.BooleanField("Event Subscription", default=True)
    paper_receipt = models.BooleanField("Do not want a paper receipt.", default=False)

    # Adopt a project information
    adopt_a_project = models.ForeignKey(AdoptAProjectDonation, blank=True, null=True, related_name='master')

    @func_attrs(allow_tags=True, short_description='CC Processed?')
    def show_trans_status(self):
        return '<a href="/donations/single/echo-response/%d/" target="_blank"><strong>%s</strong></a>' % (self.id, yesno(self.trans_status, "Yes,No"))

    @func_attrs(allow_tags=True, short_description='Adopt a Project?')
    def show_adopt_a_project(self):
        if self.adopt_a_project is not None:
            return '<a href="/admin/donorportal/donation/%d"><strong>Yes</strong></a>' % (self.adopt_a_project.id)
        else:
            return 'No'

    @func_attrs(short_description='Rcpt #')
    def receipt_number(self):
        return (15000 + self.id)

    class Spreadsheet:
        additional_fields = ()
        quickbooks = ('receipt_number', 'signup_date', 'first_name', 'last_name', 'email',
                'address_1', 'address_2', 'city', 'state', 'zipcode',
                'action_center', 'phone', 'amount', 'company',
                'company_name', 'trans_status', 'comments')

    def __unicode__(self):
        return self.first_name

    def emailRecipients(self):
        recipients = [ self.email, 'donations@vibha.org', 'office@vibha.org', ]
        if self.champion is not None:
            recipients.append(self.champion.email)
        return recipients

class HTGSignup(models.Model):

    signup_date    = models.DateTimeField("Signup date",  editable=False, auto_now=True)
    first_name     = models.CharField("First name",        max_length=100)
    last_name      = models.CharField("Last name",         max_length=100)
    email          = models.EmailField("E-mail")
    address_1      = models.CharField("Address 1",  max_length=100, blank=False)
    address_2      = models.CharField("Address 2",  max_length=100, blank=True)
    city           = models.CharField("City",       max_length=100, blank=False)
    state          = models.ForeignKey(State,                      blank=False)
    zipcode        = models.CharField("Zip code",   max_length=100, blank=False)
    country        = models.CharField("Country",    max_length=100, blank=False)
    phone          = models.CharField("Phone",      max_length=100, blank=True)
    amount         = models.DecimalField("Amount",    max_digits=9, decimal_places=2)

    # What are we going to use? check or credit card
    use_check      = models.BooleanField("Use check?")

    # Check details
    bank_name      = models.CharField("Bank name",  max_length=100, blank=True)
    aba_number     = models.CharField("ABA number", max_length=100, blank=True)
    account_number = models.TextField("Encrypted account number",  blank=True)

    # Credit card details
    cc_ac_name     = models.CharField("Name (Credit card)", max_length=100, blank=True)
    cc_number      = models.TextField("Encrypted credit card number", blank=True)
    cc_expr_month  = models.IntegerField("Expr month", blank=True, null=True, choices=vibhautilsdates.MONTH_CHOICES)
    cc_expr_year   = models.IntegerField("Expr year", blank=True, null=True)

    # Matching donations information
    company        = models.ForeignKey(Company,        blank=True, null=True)
    # company_name is valid only if (company is None)
    # company_name is used when the company does not already exist in the Company table
    company_name   = models.CharField("Company name",  blank=True,            max_length=100)

    # IP address
    ip_address     = models.IPAddressField("IP Address", blank=True)

    # Subscription information
    project_subscription = models.BooleanField("Project Subscription", default=True)
    event_subscription = models.BooleanField("Event Subscription", default=True)
    paper_receipt = models.BooleanField("Want a paper receipt?", default=False)
    referrer       = models.CharField("Referrer",   max_length=255, blank=True)
    comments       = models.TextField("Comments",   blank=True)
    
    def __str__(self):
        return self.first_name

    def emailRecipients(self):
        return [ self.email, 'htg@vibha.org', 'office@vibha.org', ]

    def save(self):
        """
        Encrypts the fields before saving them.

        The save routine should be called only once. Or else, the CC number
        and bank account number will be encrypted multiple times.
        """
        if not self.id:
            # This record has not already been saved. Being careful that we
            # do not re-encrypt stuff.
            if self.use_check:
                # Do not use CC details
                self.cc_ac_name = self.cc_number = ''
                self.cc_expr_month = self.cc_expr_year = None
                # Encrypt bank account number
                self.account_number = encrypt(self.account_number)
            else:
                # Do not use check details
                self.bank_name = self.aba_number = self.account_number = ''
                # Encrypt cc number
                self.cc_number = encrypt(self.cc_number)
        super(HTGSignup, self).save()

# vim:ts=4:sw=4:et:
