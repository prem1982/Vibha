from datetime import date,timedelta

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminDateWidget
from django.core.mail import send_mail, EmailMessage, SMTPConnection
from django.template.loader import render_to_string

from vibha.donorportal.models import Campaign
from vibha.donorportal.utils import clean_currency
from vibha.donorportal.fields import MultiEmailField
from vibha.registration.utils import ReadOnlyField
from vibha.donations.views.singledonation import generate_form_class
from vibha.utils.creditcard import transact

SingleDonationForm = generate_form_class(30)

#For debugging, only
from vibha.debug import *

class RaiseFundsForm(forms.Form):

    campaign_amount = forms.IntegerField(label='Total Campaign amount:',help_text='(Including your donation)')
    donating_amount = forms.IntegerField(label='I am donating:')

    def clean(self):
        if self.is_valid():

            if self.cleaned_data['donating_amount']<=0 or self.cleaned_data['campaign_amount']<=0:
                raise forms.ValidationError('Please enter proper values')

            if self.cleaned_data['donating_amount'] >= self.cleaned_data['campaign_amount']:
                raise forms.ValidationError('donating amount has to be lesser than campaign amount')


        return self.cleaned_data

from vibha.registration.countries import LIST_OF_COUNTRIES
class DonationAmountForm(SingleDonationForm):
    def __init__(self,request,total_amount,**kwargs):
        user = request.user
        pro = request.user.get_profile()
        initial_dict = {}
        initial_dict.update(user.__dict__)
        initial_dict.update(pro.__dict__)
        initial_dict.update(dict(address_1=pro.address1,
                                 address2=pro.address2,
                                 phone=pro.phone_number,
                                 cc_name=user.get_full_name(),
                                 ))
        super(DonationAmountForm,self).__init__(initial=initial_dict,**kwargs)
        self.fields.pop('amount_choice')
        self.fields['amount'] = ReadOnlyField(initial=total_amount)
        self.fields['amount'].widget.attrs.update({'style':'font-size:1.5em'})
        self.fields['country'].widget = forms.Select(choices=LIST_OF_COUNTRIES)
        # Hide the project and event emails fields. Set it to the profile settings value
        self.fields['project_subscription'] = forms.BooleanField(required=False, initial=pro.send_project_mails, widget=forms.HiddenInput())
        self.fields['event_subscription'] = forms.BooleanField(required=False, initial=pro.send_event_mails, widget=forms.HiddenInput())

        try:
            ip = request.META['REMOTE_ADDR']
        except:
            ip = '0.0.0.0'
        self.fields['ip_address'] = forms.CharField(required=False,max_length=256,widget=forms.HiddenInput(),initial=ip)

    def save(self,project,campaign,donation_id):
        """Do the talking to the payment processors and save a
        record in the older donation model"""
        cleaned_data = self.cleaned_data

        # Write donation details to the database
        credit_card = cleaned_data['credit_card']
        expr_month, expr_year = cleaned_data['expr_date']
        cnp_security = cleaned_data['cvv']
        amount = cleaned_data['amount']
        address_1 = cleaned_data['address_1']
        zipcode = cleaned_data['zipcode']
        ip_address = cleaned_data['ip_address']
        #company = get_object_or_none(Company, id=cleaned_data['company_id'])

        from vibha.donations.models import Donation as MasterDonation
        d = MasterDonation(
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
            #company=company,
            company_name=cleaned_data['company_name'],
            paper_receipt=cleaned_data['paper_receipt'],
            project_subscription=cleaned_data['project_subscription'],
            event_subscription=cleaned_data['event_subscription'],
            #champion=champion,
            project=project,
            adopt_a_project=donation_id,
            anonymous=cleaned_data['anonymous'])
        d.save()

        import logging
        # Process the transaction
        logging.info('donorportal_donate: expr_month: %s, expr_year: %s', expr_month, expr_year)
        if project is not None:
            logging.info('donorportal_donate: project specific donation to: %s', unicode(project))
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
            email = EmailMessage('Error while processing adopt-a-project donation, please take a look', body, 'donations@vibha.org', recipients)
            email.attach('response.html', d.trans_response, 'text/html')
            email.send(fail_silently=False)

from django.contrib.auth.models import User
qs = User.objects.all()

class MessageForm(forms.Form):
    campaign_amount = forms.IntegerField(label='Total Campaign amount:',help_text='(Your fundraising goal)')
    description = forms.CharField(label='Enter message for the campaign:', help_text='This message will be sent to chosen recipients',widget=forms.Textarea)
    to_email_field = MultiEmailField(label='Enter upto 5 email ids to which you want to send this message',help_text='Seperate emails by comma',widget=forms.Textarea)
    campaign_end_date = forms.DateField(widget=AdminDateWidget(),initial=date.today()+timedelta(days=31),help_text='Defaults to 31 days')
    ##to_field = forms.ModelMultipleChoiceField(label='Choose',queryset=qs)

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        for field in self.fields.itervalues():
            try:
                if field.widget.input_type == 'text':
                    field.widget.attrs['class'] = ' '.join([field.widget.attrs.setdefault('class',''),'textbox'])
            except:
                pass

    def clean(self):
        if self.is_valid():
            if self.cleaned_data['campaign_amount']<=0:
                raise forms.ValidationError('Invalid campaign amount')

        return self.cleaned_data

from contact_form.forms import AkismetContactForm

class AkismetInitContactForm(AkismetContactForm,forms.Form):
    def __init__(self,request,*args,**kwargs):
        init_values = {'name' : request.user.get_full_name() or request.user.username,
                       'email' : request.user.email
                       }
        init_dict = kwargs.get('initial',{})
        init_dict.update(init_values)
        kwargs['initial'] = init_dict
        super(AkismetInitContactForm,self).__init__(request=request,*args,**kwargs)

        for field in self.fields.itervalues():
            try:
                if field.widget.input_type == 'text':
                    field.widget.attrs['class'] = ' '.join([field.widget.attrs.setdefault('class',''),'textbox'])
            except:
                pass


class TellFriendsForm(AkismetInitContactForm):
    to_email = MultiEmailField(label='Recipient Emails',help_text='Max 5 email ids')
    project_info = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self,request,*args,**kwargs):
        super(TellFriendsForm,self).__init__(request,*args,**kwargs)

    def clean_to_email(self):
        if len(self.cleaned_data['to_email'])>5:
            raise forms.ValidationError('Please enter a maximum of 5 email ids')
        return self.cleaned_data['to_email']

    def save(self,subject=None):
        if subject is None:
            subject = '%s wants you to learn more about out this Vibha Project'%self.cleaned_data['name']
        message=self.cleaned_data['body'] + self.cleaned_data['project_info']
        from_email=settings.DEFAULT_FROM_EMAIL

        # Split into several messages so recipients dont see the other recipients
        msg = []
        for recipient in self.cleaned_data['to_email']:
            m = EmailMessage(subject,message,from_email,[recipient])
            m.content_subtype = "html"
            msg.append(m)

        connection = SMTPConnection()
        connection.send_messages(msg)

