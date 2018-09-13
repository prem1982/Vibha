# $Id: views.py 406 2007-12-03 02:38:44Z suriya $

# Create your views here.

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from datetime import date, timedelta
from django.contrib.syndication.feeds import Feed

from vibha.projects.models import Project, Report

def map(request):
    """ Default behavior is to display all mappable projects """
    if request.REQUEST.has_key('projects'):
        if request.REQUEST['projects'] == 'past':
            projectS = [ p for p in Project.past_projects.all() if p.canBeMapped() ]
            projtype = 'past'
        else:
            projectS = [ p for p in Project.current_projects.all() if p.canBeMapped() ]
            projtype = 'current'
    else:
        projectS = [ p for p in Project.objects.all() if p.canBeMapped() ]
        projtype = 'all'

    count = len(projectS)
    locationS = [ p.infoBoxCodeForMap(i, count) for i,p in enumerate(projectS) ]
    return render_to_response('projects/maps/listing.dmpl', {'locationS': locationS, 'projects': projtype})

def detail(request, slug):
    """Display the details for a project."""
    project = get_object_or_404(Project, slug=slug)
    authenticated = request.user.is_authenticated()
    """ Show only reports of type 
    Quaterly, Half-yearly, Annual and Newsletter"""
    reportS = project.report_set.filter(show=True).filter(report_type__in=[5,6,7,11,17]).order_by('-report_date')
    fundingS = project.projectfundingdetail_set.all().order_by('-begin_date')
    picture = project.get_random_picture()
    canBeMapped = project.canBeMapped()
    return render_to_response('projects/detail.dmpl',
            {'project':  project,
             'reportS':  reportS,
             'fundingS': fundingS,
             'picture':  picture,
             'canBeMapped': canBeMapped,
             'authenticated': authenticated})

@staff_member_required
def factsheet(request, slug):
    """Display the fact sheet for a project. This is used by office@vibha to
    send disbursals"""
    project = get_object_or_404(Project, slug=slug)
    authenticated = request.user.is_authenticated()
    reportS = project.report_set.all().order_by('-report_date')
    organization = project.organization
    lead = project.internal_contact.contact
    fundingS = project.projectfundingdetail_set.all()
    disbursalS = project.disbursal_set.all()
    return render_to_response('projects/factsheet.dmpl',
            {'project':      project,
             'reportS':      reportS,
             'lead':         lead,
             'fundingS' :    fundingS,
             'disbursalS':   disbursalS,
             'organization': organization,})

@staff_member_required
def agreement(request, slug):
    from pdfagreement import pdfagreement
    """A PDF file with the agreement between Vibha and the organization."""
    project = get_object_or_404(Project, slug=slug)
    organization = project.organization
    try:
        funding = project.projectfundingdetail_set.latest('begin_date')
    except ObjectDoesNotExist:
        return render_to_response('flatpage.html',
            {'content': '<p>No funding detail available for this project.</p>',
             'title':   'Partnership agreement document',})
    today = date.today()
    context = {
        'project':            project,
        'organization':       organization,
        'today':              today,
        'fiveyearsfromtoday': today + timedelta(days=(365*5) + 1),
        'funding':            funding,
    }
    filename = 'partnership-agreement-%s.pdf' % slug
    return pdfagreement(filename, context)

def gallery(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render_to_response('projects/gallery.html', {'project': project})

def gallery_xml(request, slug):
    project = get_object_or_404(Project, slug=slug)
    pictureS = project.picture_set.filter(show=True)
    return render_to_response('projects/gallery.xml',
        {'project':  project,
         'pictureS': pictureS,})

class LatestReports(Feed):
    title = 'Vibha.org project reports'
    link = '/project-reports/'
    description = "Updates on reports recently uploaded to projects.vibha.org"

    def items(self):
        return Report.objects.order_by('-upload_date')[:10]

    def item_link(self, report):
        return report.get_admin_url()

    def item_pubdate(self, report):
        return report.upload_date

from django import forms
from django.forms.widgets import *
from django.template.loader import render_to_string
from vibha.utils.shortcuts import our_flatpage, accepts_cookies
from vibha.utils.newforms.formwrappers import form_with_captcha
from django.http import HttpResponseRedirect
from django.core.mail import send_mail

class ProjectLeadContactForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField(required=False)
    message = forms.CharField(widget=Textarea())

def contactlead(request,slug):
    project = get_object_or_404(Project, slug=slug)
    Form = form_with_captcha(ProjectLeadContactForm,request)

    if request.method == 'POST':
        # Process the form
        if not accepts_cookies(request):
            return our_flatpage('Please enable cookies and try again.')
        else:
            form = Form(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                
                # Send email to project team
                msg = render_to_string('projects/project_lead_contact_email.dmpl',\
                        {'project':project, 'from':data['email'],'name':data['name'],\
                        'phone':data['phone'],'msg':data['message']})
                send_mail('Vibha Project Information Request',msg,'projects@vibha.org',\
                        ['projects@vibha.org',project.internal_contact.contact.email,\
                        'amenon81@gmail.com','lux@vibha.org'],\
                        fail_silently=False)
                
                # Send thank you email to patron
                msg = render_to_string('projects/thanks_for_contacting_us_email.dmpl',\
                        {'name':data['name']})
                send_mail('Thank you for your interest in Vibha',msg,\
                        'projects@vibha.org',[data['email']], fail_silently=False)
                
                return HttpResponseRedirect('/projects/thanks_for_contacting_us')
            else:
                # Show the form with error
                return render_to_response('projects/project_lead_contact_form.dmpl',\
                        {'form':form,'project':project})
    else:
        # Show blank form
        form = Form()
        accepts_cookies(request)
        return render_to_response('projects/project_lead_contact_form.dmpl',\
                {'form':form,'project':project})

def thanks_for_contacting_us(request):
    return render_to_response('projects/thanks_for_contacting_us.dmpl')


# vim:ts=4:sw=4:et:ai:
