
# $Id: complexformprocessing.py 430 2008-01-27 02:19:22Z suriya $

"""
ComplexFormProcessing application.

This does the following.

   * Display a HTML form (automatically with captcha if necessary)
   * After the users enters the data, show a confirmation page
   * Finally, save it in the database, send and email, do additional
     processing.

Provide a Form class, a function that returns a Model object from the
Form's cleaned_data, and templates for the form and email addresses.

Usage:
    Instantiate a ComplexFormProcessing object and use it in the URLconf
    like this.
    cfp = ComplexFormProcessing(MyForm, form_to_model, ...)
    (r'^url/$', cfp.view),

The form template should accept (atleast) the following variables: form. It
can accept other template variables specified in extra_form_template_args.

The email template should accept (atleast) the following variables: model.
It can accept other template variables specified in extra_form_template_args.
"""

from vibha.utils.shortcuts import our_flatpage, accepts_cookies
from django.shortcuts import render_to_response
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect
from formwrappers import form_with_captcha, form_with_ipaddress

class ComplexFormProcessing:

    def __init__(self, form_session_name, form_class, cleaned_data_2_model, form_template,
            confirm_template, model_2_should_send_email, email_template, email_subject, email_sender,
            model_2_redirect_url, do_captcha=False, record_ip_addr=False, email_html_template=None):
        self.form_session_name= form_session_name
        self.form_class = form_class
        self.cleaned_data_2_model = cleaned_data_2_model
        self.form_template = form_template
        self.confirm_template = confirm_template
        self.model_2_should_send_email = model_2_should_send_email
        self.email_template = email_template
        self.email_html_template = email_html_template
        self.email_subject = email_subject
        self.email_sender = email_sender
        self.model_2_redirect_url = model_2_redirect_url
        self.do_captcha = do_captcha
        self.record_ip_addr = record_ip_addr

    def create_form_class(self, request):
        """Create the form class based on what is needed."""
        Form = self.form_class
        if self.do_captcha:
            Form = form_with_captcha(Form, request)
        if self.record_ip_addr:
            Form = form_with_ipaddress(Form, request)
        return Form

    def show_empty_form(self, request, initial, extra_form_template_args):
        Form = self.create_form_class(request)
        form = Form(initial=initial)
        accepts_cookies(request)
        template_args = {'form': form}
        template_args.update(extra_form_template_args)
        return render_to_response(self.form_template, template_args)

    def confirm_details(self, request, extra_form_template_args):
        Form = self.create_form_class(request)
        form = Form(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            request.session[self.form_session_name] = cleaned_data
            # Show form confirmation page
            template_args = {'cleaned_data': cleaned_data}
            template_args.update(extra_form_template_args)
            return render_to_response(self.confirm_template, template_args)
        else:
            # Show form with errors
            template_args = {'form': form}
            template_args.update(extra_form_template_args)
            return render_to_response(self.form_template, template_args)

    def do_processing(self, request, extra_form_template_args):
        cleaned_data = request.session.get(self.form_session_name, None)
        if cleaned_data is not None:
            del request.session[self.form_session_name]
            model = self.cleaned_data_2_model(cleaned_data)
            if self.model_2_should_send_email(model) and self.email_template:
                template_args = {'model': model}
                template_args.update(extra_form_template_args)
                text_content = render_to_string(self.email_template, template_args)
                recipients = model.emailRecipients()
                
                msg = EmailMultiAlternatives(self.email_subject, text_content, self.email_sender, recipients)
                if self.email_html_template:
                    html_content = render_to_string(self.email_html_template, {'model': model})
                    msg.attach_alternative(html_content, "text/html")
                msg.send()

            redirect_url = self.model_2_redirect_url(model)
            return HttpResponseRedirect(redirect_url)
        else:
            return our_flatpage('Some error occurred.')

    def view(self, request, initial={}, extra_form_template_args={}):
        if request.method == 'POST':
            if accepts_cookies(request):
                step = request.POST.get('form_step', 0)
                if step == 'confirm_details': return self.confirm_details(request, extra_form_template_args)
                elif step == 'do_processing': return self.do_processing(request, extra_form_template_args)
                else: return our_flatpage('Some error occured')
            else:
                return our_flatpage("Please enable cookies and try again.")
        else:
            return self.show_empty_form(request, initial, extra_form_template_args)
