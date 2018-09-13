
# $Id: simpleformprocessing.py 430 2008-01-27 02:19:22Z suriya $

"""
SimpleFormProcessing application.

This does the following.

   "Display a HTML form (automatically with captcha if necessary), save it
   as a model in the database, send an email if asked to do so."

Provide a Form class, a function that returns a Model object from the
Form's cleaned_data, and templates for the form and email addresses.

Usage:
    Instantiate a SimpleFormProcessing object and use it in the URLconf
    like this.
    sfp = SimpleFormProcessing(MyForm, form_to_model, ...)
    (r'^url/$', sfp.view),
"""

from vibha.utils.shortcuts import our_flatpage, accepts_cookies
from django.shortcuts import render_to_response
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect
from formwrappers import form_with_captcha, form_with_ipaddress

class SimpleFormProcessing:

    def __init__(self, form_class, form_2_model, form_template,
            email_template, email_subject, email_sender, redirect_url,
            do_captcha=False, record_ip_addr=False, email_html_template=None):
        self.form_class = form_class
        self.form_2_model = form_2_model
        self.form_template = form_template
        self.email_template = email_template
        self.email_html_template = email_html_template
        self.email_subject = email_subject
        self.email_sender = email_sender
        self.redirect_url = redirect_url
        self.do_captcha = do_captcha
        self.record_ip_addr = record_ip_addr

    def view(self, request, initial={}):
        Form = self.form_class
        if self.do_captcha:
            Form = form_with_captcha(Form, request)
        if self.record_ip_addr:
            Form = form_with_ipaddress(Form, request)
        if request.method == 'POST':
            # Try processing the form
            if self.do_captcha and not accepts_cookies(request):
                return our_flatpage('Please enable cookies and try again.')
            else:
                form = Form(request.POST)
                if form.is_valid():
                    # The form is correct, process it
                    model = self.form_2_model(form)
                    if self.email_template:
                        text_content = render_to_string(self.email_template, {'model': model})
                        recipients = model.emailRecipients()
                        try:
                            bcc_recipients = model.emailBCCRecipients()
                        except:
                            bcc_recipients = None
                        msg = EmailMultiAlternatives(self.email_subject, text_content, self.email_sender,
                                recipients, bcc_recipients)

                        if self.email_html_template:
                            html_content = render_to_string(self.email_html_template, {'model': model})
                            msg.attach_alternative(html_content, "text/html")

                        msg.send()

                    return HttpResponseRedirect(self.redirect_url)
                else:
                    # Show the form with errors
                    return render_to_response(self.form_template, {'form': form})
        else:
            # Show the empty form
            form = Form(initial=initial)
            if self.do_captcha:
                accepts_cookies(request)
            return render_to_response(self.form_template, {'form': form})
