
# $Id: formwrappers.py 407 2007-12-03 05:20:21Z suriya $

from django import forms
from vibha.utils.captcha import is_human, check_captcha

__all__ = ('form_with_ipaddress', 'form_with_captcha', )

def form_with_ipaddress(form_class, request):
    """Adds an IP address field to a form

    How to use this function.
    Wherever you use a form named FooForm, like this

        form = FooForm(...)
        use form

    replace it with

        FooFormWithIPaddress = form_with_ipaddress(FooForm, request)
        form = FooFormWithIPaddress(...)
        use form
    """

    assert 'ip_address' not in form_class.base_fields

    class FormWithIPAddress(form_class):
        ip_address = forms.CharField(required=False, max_length=256, widget=forms.HiddenInput())

        def clean_ip_address(self):
            # It is possible that REMOTE_ADDR might not be set, maybe due
            # to configuration errors, or because we are in testing mode.
            # Do not fail violently
            try:
                return request.META['REMOTE_ADDR']
            except KeyError:
                return '0.0.0.0'

    return FormWithIPAddress

def form_with_captcha(form_class, request):
    """Adds a captcha field to a form, if necessary (the person has not
    already proved that they are a human being).

    How to use this function.
    Wherever you use a form named FooForm, like this

        form = FooForm(...)
        use form

    replace it with

        FooFormWithCapcha = form_with_captcha(FooForm, request)
        form = FooFormWithCapcha(...)
        use form

    The template that renders the form has to be modified to show the
    captcha field as well. Include a captcha field in a template by

        {% captcha_field form %}
    """

    assert 'captcha' not in form_class.base_fields
    assert 'is_bot' not in form_class.base_fields

    if is_human(request):
        return form_class
    else:
        class FormWithCaptcha(form_class):
            captcha = forms.CharField(max_length=10, label='Word', help_text='Enter the text in the image above. This word verification helps Vibha discourage spammers.')
            is_bot = True

            def clean_captcha(self):
                if check_captcha(request, self.cleaned_data['captcha']):
                    self.is_bot = False
                else:
                    raise forms.ValidationError(u'Incorrect captcha value')
                # Always return None, we do not need the captcha value
                return None

        return FormWithCaptcha

# vim:ts=4:sw=4:et:ai:
