
# $Id: views.py 468 2008-05-22 07:38:05Z suriya $

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from django import forms
from django.core.mail import send_mail
from vibha.dream.models import Event
from vibha.utils.newforms.simpleformprocessing import SimpleFormProcessing

@staff_member_required
def index(request):
    """Show the list of all approved events."""
    eventS = list(Event.objects.all())
    return render_to_response('dream/listing.dmpl',
            {'eventS': eventS})

def event(request, slug):
    event = get_object_or_404(Event, slug=slug)
    authenticated = request.user.is_authenticated()
    return render_to_response('dream/event.dmpl', {
            'event': event, 'authenticated': authenticated, })

# @staff_member_required
# def donations(request, slug):
#     """List of all donations for this dream registry event."""
#     event = get_object_or_404(Event, slug=slug)
#     donationS = e
#     return render_to_response('dream/donations.html', {

########################################################
# Process a new event
########################################################
class EventForm(forms.Form):
    email          = forms.EmailField(label="E-mail")
    honoree        = forms.CharField(label="Honoree",           max_length=100)
    event_date     = forms.DateField(label="Event date")
    short_title    = forms.CharField(label="Celebration name",  max_length=100)
    url            = forms.CharField(label="Event URL", max_length=256, required=False)
    message        = forms.CharField(label="Invitation message", widget=forms.Textarea())

def eventform_2_model(form):
    if not form.is_valid():
        return None
    data = form.cleaned_data
    event = Event(email=data['email'], honoree=data['honoree'],
            event_date=data['event_date'], short_title=data['short_title'],
            url=data['url'], message=data['message'])
    event.save()
    return event

sfp = SimpleFormProcessing(
        form_class=EventForm,
        form_2_model=eventform_2_model,
        form_template='dream/create_event_form.dmpl',
        email_template='dream/response_email.dmpl',
        email_subject='Hello World',
        email_sender='ithelpdesk@vibha.org',
        redirect_url='/dream/thanks/',
        do_captcha=True)

# vim:nowrap:ts=4:sw=4:et:
