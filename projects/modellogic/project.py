
# $Id: project.py 421 2007-12-25 20:33:28Z suriya $

from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import yesno
from vibha.projects.models import Report
from datetime import timedelta, date
from vibha.utils.decorators import func_attrs
from vibha.utils.templatetags.utils import doslinebreaksbr
from django.template.defaultfilters import truncatewords, escape, escapejs

from random import choice

# The following functions should actually, be methods inside
# vibha.projects.models.Project
# They are here, so that the organization is a little bit cleaner.

__all__ = (
    'has_funding_details',
    'has_pictures',
    'has_proposal',
    'latest_report',
    'monitoring_report_0',
    'monitoring_report_1',
    'monitoring_report_2',
    'get_relevant_reports',
    'next_monitoring_visit_due',
    'id3',
    'get_absolute_url',
    'get_factsheet_url',
    'get_admin_url',
    'get_gallery_url',
    'get_gallery_xml_url',
    'get_random_picture',
    'canBeMapped',
    'infoBoxCodeForMap',
    'show_internal_contact_info',
    'show_internal_contact_email',
    'show_internal_contact_phone',
    'show_organization',
    'show_organization_info',
    'show_project_address',
    'show_focus_areas',
    'show_project_desc',
    'show_project_picture',
)

########################################################################
# Project overview page
########################################################################

@func_attrs(short_description='Funding')
def has_funding_details(self):
    return yesno(self.projectfundingdetail_set.count() > 0, "Yes,")

@func_attrs(allow_tags=True, short_description='Pics')
def has_pictures(self):
    pics = self.picture_set.count()
    if pics > 0:
        return '<a href="%s">%d</a>' % (self.get_gallery_url(), pics)
    else:
        return ''

@func_attrs(allow_tags=True, short_description='Proposal?')
def has_proposal(self):
    try:
        proposal = self.report_set.filter(report_type=Report.x00_PROPOSAL).latest('report_date')
        return '<a href="%s">Yes</a>' % proposal.get_report_file_url_custom()
    except ObjectDoesNotExist:
        return ''

# Having this query outside the function, so we do not have to compute this
# every time
_LATEST_REPORT_QUERY = (
        Q(report_type=Report.x05_QUARTERLY_REPORT)   |
        Q(report_type=Report.x06_ANNUAL_REPORT)      |
        Q(report_type=Report.x11_HALF_YEARLY_REPORT))
@func_attrs(allow_tags=True, short_description='Latest report')
def latest_report(self):
    try:
        report = self.report_set.filter(_LATEST_REPORT_QUERY).latest('report_date')
        return '<a href="%s">%s</a>' % (report.get_report_file_url_custom(), report.report_date)
    except ObjectDoesNotExist:
        return ''

@func_attrs(short_description='Project Lead')
def show_internal_contact_info(self):
    return '%s %s<br/>Email: %s <br/> Ph: %s'%(self.internal_contact.contact.first_name,self.internal_contact.contact.last_name,self.internal_contact.contact.email,self.internal_contact.contact.phone)
@func_attrs(short_description='Email Address')
def show_internal_contact_email(self):
    return self.internal_contact.contact.email
@func_attrs(short_description='Phone Number')
def show_internal_contact_phone(self):
    return self.internal_contact.contact.phone

@func_attrs(allow_tags=True, short_description='Organization')
def show_organization(self):
    return '<a href="/admin/projects/organization/%d/" target="_blank">%s</a>' % (self.organization.id, self.organization)
@func_attrs(short_description='Organization')
def show_organization_info(self):
    organization_info = '%s<br/>Contact: %s %s<br/>Email: %s <br/> Ph: %s<br/>' % (self.organization.name,self.organization.contact.first_name,self.organization.contact.last_name,self.organization.email,self.organization.phone)
    if self.organization.url:
        organization_info += 'Website: <a href="%s">%s</a><br/>' % (self.organization.url,self.organization.url)
    if self.organization.address_1:
        organization_info += 'Address: <br />&nbsp; %s <br/>&nbsp; ' % self.organization.address_1
        if self.organization.address_2:
            organization_info += '%s <br/>&nbsp; ' % self.organization.address_2
        if self.organization.address_3:
            organization_info += '%s <br/>&nbsp; ' % self.organization.address_3
        if self.organization.city:
            organization_info +=  '%s %s <br/>'%(self.organization.city, self.organization.zipcode)
        if self.organization.state:
            organization_info += '&nbsp; %s' % self.organization.state
    return organization_info

@func_attrs(short_description='Project Address')
def show_project_address(self):
    if self.organization.address_1:
        address = self.organization.address_1
    else:
        return None
    if self.organization.address_2:
        address += '<br/>' + self.organization.address_2
    if self.organization.address_3:
        address += '<br/>' + self.organization.address_3
    if self.organization.city:
        address +=  '<br/>%s %s'%(self.organization.city, self.organization.zipcode)
    if self.organization.state:
        address += '&nbsp; %s' % self.organization.state

    return address

@func_attrs(short_description='Focus Areas')
def show_focus_areas(self):
    fareas = ''
    for f in self.focus_areas.all():
        fareas += str(f)+ '<br/>'
    return fareas

@func_attrs(short_description='Project Description')
def show_project_desc(self):
    return '%s' % self.desc_html


########################################################################
# Monitoring report stuff
########################################################################
def _monitoring_report_i(self, i):
    try:
        report = self.report_set.filter(report_type=Report.x09_MONITORING_REPORT).order_by('-report_date')[i]
        return '<a href="%s">%s</a>' % (report.get_report_file_url_custom(), report.report_date)
    except IndexError:
        return ''

@func_attrs(allow_tags=True, short_description='Latest monitoring')
def monitoring_report_0(self):
    return _monitoring_report_i(self, 0)

@func_attrs(allow_tags=True, short_description='Report 1')
def monitoring_report_1(self):
    return _monitoring_report_i(self, 1)

@func_attrs(allow_tags=True, short_description='Report 2')
def monitoring_report_2(self):
    return _monitoring_report_i(self, 2)

SIX_MONTHS = timedelta(days=180)
TODAY = date.today()
@func_attrs(short_description='Next visit')
def next_monitoring_visit_due(self):
    try:
        report = self.report_set.filter(report_type=Report.x09_MONITORING_REPORT).latest('report_date')
        return max(report.report_date + SIX_MONTHS, TODAY)
    except ObjectDoesNotExist:
        return TODAY

def get_relevant_reports(self):
    return self.report_set.filter(show=True).filter(report_type__in=[5,6,7,11]).order_by('-report_date')
    

########################################################################
# Project ID padded
########################################################################
@func_attrs(short_description='Id')
def id3(self):
    """Project ID padded to three digits."""
    return '%03d' % self.id

########################################################################
# Some URLs
########################################################################
def get_absolute_url(self):
    return '/projects/%s/' % self.slug

def get_factsheet_url(self):
    return '%sfactsheet/' % self.get_absolute_url()

def get_admin_url(self):
    return '/admin/projects/project/%d/' % self.id


########################################################################
# Related to pictures
########################################################################
def get_gallery_url(self):
    return '/projects/%s/gallery/' % self.slug

def get_gallery_xml_url(self):
    return '/projects/%s/galleryxml/' % self.slug

def get_random_picture(self):
    p = self.picture_set.order_by('?')[:1]
    if p:
        return p[0]
    else:
        return None

@func_attrs(short_description='Pictures')
def show_project_picture(self):
    try:
        return '<a href="%s" target="_blank"><img src="%s"></a>' % (self.get_gallery_url(), self.get_random_picture().thumbnail.url)
    except:
        return 'Not Available'



########################################################################
# Related to maps
########################################################################
def canBeMapped(self):
    loc = self.location
    return (loc.state.country.name == 'India') and (loc.latitude is not None) and (loc.longitude is not None)

def infoBoxCodeForMap(self, index=None, indexCount=None):
    if (index is None) or (indexCount is None) or not self.canBeMapped():
        return None
    js_url = self.get_absolute_url()
    prev_index = (index + indexCount - 1) % indexCount
    next_index = (index + indexCount + 1) % indexCount
    picture = self.get_random_picture()
    if picture:
        div_name = 'mapinfo'
        picture_code = '<div class="thumbnail"><img src="%s" alt="%s"/></div>' % (picture.thumbnail.url, escapejs(doslinebreaksbr(escape(picture.desc))))

    else:
        div_name = 'mapinfo-nopic'
        picture_code = ''
    code = r"""
        {
          lat: %s,
          lng: %s,
          current_project: %d,
          code: '                                                                              \
                  <div class="%s">                                                                   \
                  <h3> <a target="_blank" href="%s"> %s, %s </a> </h3>                             \
                  %s                                                                               \
                  <p> %s </p>                                                                      \
                  <div class="bottom">                                                             \
                  <div class="bottom-left"><a target="_blank" href="%s">Read More</a></div>      \
                  <div class="bottom-right">                                                     \
                  </div>                                                                         \
                  <br style="clear: both;" />                                                    \
                  </div>                                                                           \
                  </div>'
        }""" % (self.location.latitude, self.location.longitude, self.is_current(), div_name,
                js_url, escapejs(escape(self.name)),
                escapejs(escape(self.location.name)), picture_code,
                escapejs(doslinebreaksbr(escape(truncatewords(self.desc, 30)))), js_url)
    return code
