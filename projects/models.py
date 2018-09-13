# $Id: models.py 460 2008-04-02 22:18:42Z suriya $

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.encoding import smart_unicode

from vibha.utils.decorators import func_attrs

import os
from StringIO import StringIO
from random import choice
import shutil
import re
import datetime

# Almost constant data. The tables Country, State, FocusArea,
# FocusSubArea and ActionCenter contain data that remain almost
# constant.

class Country(models.Model):
    name = models.CharField("Name", max_length=100)

    class Admin:
        list_display = ('name', )

    class Meta:
        verbose_name_plural = 'countries'

    def __unicode__(self):
        return self.name


class State(models.Model):
    name    = models.CharField("Name",                      max_length=100)
    postal  = models.CharField("Postal code",   blank=True, max_length=10)
    country = models.ForeignKey(Country)

    class Admin:
        list_display = ('name', 'postal', 'country')

    class Meta:
        ordering = ('country', 'name', )


    def __unicode__(self):
        return self.name
#         return '%s, %s' % (self.name, self.country)


class ActionCenter(models.Model):
    """Model for an ActionCenter.

    This table should contain an action center named None"""
    name = models.CharField("Name", max_length=100)
    url  = models.URLField("URL",   verify_exists=False, blank=True)

    class Admin:
        list_display = ('name', 'url')

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return self.name


class FocusArea(models.Model):
    class Admin: pass
    name = models.CharField("Name", max_length=50)
    desc = models.TextField("Description", blank=True)

    def save(self):
        """Automatically add a FocusSubArea when a FocusArea is added."""
        super(FocusArea, self).save()
        try:
            subarea = self.focussubarea_set.get(name="General")
        except ObjectDoesNotExist:
            subarea = subarea = FocusSubArea(focus=self, name="General")
            subarea.save()
        except AssertionError:
            # more than one object was found. Huh, something should be
            # done
            pass

    def __unicode__(self):
        return self.name


class FocusSubArea(models.Model):
    focus = models.ForeignKey(FocusArea)
    name  = models.CharField("Name", max_length=50)
    desc  = models.TextField("Description", blank=True)

    class Admin:
        list_display = ('focus', 'name')

    def __unicode__(self):
        return unicode(self.focus) + u": " + self.name

# Now come all the interesting tables.

class Contact(models.Model):
    first_name    = models.CharField("First name",        max_length=100)
    last_name     = models.CharField("Last name",         max_length=100)
    email         = models.EmailField("E-mail")
    alt_email     = models.EmailField("Alternate E-mail", blank=True)
    phone         = models.CharField("Phone",             max_length=100)
    alt_phone     = models.CharField("Alternate Phone",   blank=True,    max_length=100)
    fax           = models.CharField("Fax",               blank=True,    max_length=100)
    address_1     = models.CharField("Address 1",         blank=True,    max_length=255)
    address_2     = models.CharField("Address 2",         blank=True,    max_length=255)
    address_3     = models.CharField("Address 3",         blank=True,    max_length=255)
    city          = models.CharField("City/District",     blank=True,    max_length=100)
    zipcode       = models.CharField("Zip Code",          blank=True,    max_length=20)
    state         = models.ForeignKey(State,              blank=True,    null=True)

    class Admin:
        list_display = ('first_name', 'last_name', 'email', 'phone')

    class Meta:
        ordering = ('first_name',)

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

class Volunteer(models.Model):
    contact       = models.ForeignKey(Contact)
    action_center = models.ForeignKey(ActionCenter, blank=True, null=True)

    class Admin:
        list_display = ('contact', 'action_center')

    def __unicode__(self):
        return u"%s (%s)" % (self.contact, self.action_center)

class ExternalContact(models.Model):
    """This represents a person outside Vibha.

    Right now, there is no additional information to be stored about
    that person, other than whatever is present in the Contact table."""
    contact = models.ForeignKey(Contact)

    class Admin: pass

    def __unicode__(self):
        return unicode(self.contact)

class Location(models.Model):
    x_00_UNKNOWN,    \
    x_01_URBAN,      \
    x_02_RURAL,      \
    x_03_SEMI_URBAN, \
    x_04_TRIBAL,     = xrange(5)

    LOCATION_TYPE_CHOICES = (
        (x_00_UNKNOWN,     "Unknown"),
        (x_01_URBAN,       "Urban"),
        (x_02_RURAL,       "Rural"),
        (x_03_SEMI_URBAN,  "Semi-urban"),
        (x_04_TRIBAL,      "Tribal"),
    )

    name      = models.CharField("Name",             max_length=100)
    type      = models.IntegerField("Location type", choices=LOCATION_TYPE_CHOICES)
    state     = models.ForeignKey(State)
    latitude  = models.DecimalField("Latitude",        max_digits=20, decimal_places=10, blank=True, null=True,
                help_text="Latitude in decimal, 30 deg 18 minute North is 30.300474")
    longitude = models.DecimalField("Longitude",       max_digits=20, decimal_places=10, blank=True, null=True,
                help_text="Longitude in decimal, 97 deg 44 minute West is -97.747247")
    comments  = models.TextField("Comments",         blank=True)

    class Admin:
        list_display = ('name', 'state', 'type', 'latitude', 'longitude', )

    def __unicode__(self):
        return self.name


class Organization(models.Model):
    x00_UNKNOWN,  \
    x01_PENDING,  \
    x02_APPROVED, \
    x03_NA,       = xrange(4)

    FCRA_STATUS_CHOICES = (
        (x00_UNKNOWN,  "Unknown"),
        (x01_PENDING,  "Pending"),
        (x02_APPROVED, "Approved"),
        (x03_NA,       "Not Applicable (US organization)"),
    )

    name      = models.CharField("Name",   max_length=200)
    url       = models.URLField("URL",     blank=True,  verify_exists=False)
    email     = models.EmailField("E-mail")
    alt_email = models.EmailField("Alternate E-mail", blank=True)
    phone     = models.CharField("Phone",             max_length=100)
    alt_phone = models.CharField("Alternate Phone",   blank=True,    max_length=100)
    fax       = models.CharField("Fax",               blank=True,    max_length=100)
    address_1 = models.CharField("Address 1",         blank=True,    max_length=255)
    address_2 = models.CharField("Address 2",         blank=True,    max_length=255)
    address_3 = models.CharField("Address 3",         blank=True,    max_length=255)
    city      = models.CharField("City/District",     blank=True,    max_length=100)
    state     = models.ForeignKey(State,              blank=True,    null=True)
    zipcode   = models.CharField("Zip Code",          blank=True,    max_length=20)
    contact   = models.ForeignKey(Contact)
    contact_title = models.CharField("Contact title", max_length=100, blank=True)
    tax_id    = models.CharField("Tax ID",            max_length=100, blank=True)
    fcra      = models.CharField("FCRA No.",          max_length=100, blank=True)
    fcra_status = models.IntegerField("FCRA Status",  choices=FCRA_STATUS_CHOICES)
    soc_reg   = models.CharField("Society Reg. No.",  max_length=100, blank=True)
    focus_areas = models.ManyToManyField(FocusSubArea)
    bank_name =  models.CharField("Bank",              max_length=100, blank=True)
    bank_address = models.CharField("Bank address",    max_length=100, blank=True)
    bank_ac_name = models.CharField("Bank A/c name",   max_length=100, blank=True)
    bank_ac_num  = models.CharField("Bank A/c number", max_length=100, blank=True)
    bank_phone   = models.CharField("Bank phone",      max_length=100, blank=True)
    bank_xfer    = models.TextField("Bank Xfer Info",  blank=True,
                   help_text="Bank transfer details, information like routing number, etc.")

    class Admin:
        list_display = ('name', 'url', 'contact')

    def __unicode__(self):
        return self.name

    def get_admin_url(self):
        return '/admin/projects/organization/%d/' % self.id


class CurrentProjectsManager(models.Manager):
    """Gets all projects that are ongoing.

    This is a subclass of manager. It filters the current projects from the
    list of all projects in the Projects table."""
    def get_query_set(self):
        q = super(CurrentProjectsManager, self).get_query_set()
        lst = [ i.id for i in q if i.is_current() ]
        # filter(id__in=lst) does not work if lst is empty. So we have
        # this hack below
        if len(lst) == 0:
            # all rows have id >= 0, the command below returns and empty QuerySet
            return q.filter(id__lt=0)
        else:
            return q.filter(id__in=lst)

class PastProjectsManager(models.Manager):
    """Gets all projects that are completed/discontinued

    This is a subclass of manager. It filters the past projects from the
    list of all projects in the Projects table."""
    def get_query_set(self):
        q = super(PastProjectsManager, self).get_query_set()
        lst = [ i.id for i in q if i.is_past() ]
        # filter(id__in=lst) does not work if lst is empty. So we have
        # this hack below
        if len(lst) == 0:
            # all rows have id >= 0, the command below returns and empty QuerySet
            return q.filter(id__lt=0)
        else:
            return q.filter(id__in=lst)

class ActiveProjectsManager(models.Manager):
    """Gets all projects that are not marked completed/discontinued

    This is a subclass of manager. It filters the past projects from the
    list of all projects in the Projects table."""
    def get_query_set(self):
        q = super(ActiveProjectsManager, self).get_query_set()
        lst = [ i.id for i in q if not i.is_past() ]
        # filter(id__in=lst) does not work if lst is empty. So we have
        # this hack below
        if len(lst) == 0:
            # all rows have id >= 0, the command below returns and empty QuerySet
            return q.filter(id__lt=0)
        else:
            return q.filter(id__in=lst)

class Tag(models.Model):
    """Tags for reports and pictures."""

    name = models.CharField("Name", max_length=50)

    class Admin:
        pass

    def __unicode__(self):
        return self.name

class Report(models.Model):
    x00_PROPOSAL,              \
    x01_QUESTION_AND_ANSWER,   \
    x02_VOLUNTEER_SITE_VISIT,  \
    x03_PICTURES,              \
    x04_AUDIT_REPORT,          \
    x05_QUARTERLY_REPORT,      \
    x06_ANNUAL_REPORT,         \
    x07_NEWSLETTER,            \
    x08_COMMUNICATION,         \
    x09_MONITORING_REPORT,     \
    x10_PARTNERSHIP_AGREEMENT, \
    x11_HALF_YEARLY_REPORT,    \
    x12_PROJECT_SELECTION_TEMPLATE, \
    x13_NTT,                    \
    x14_REJECT_DESCRIPTION,     \
    x15_BOARD_DECISION_MINUTES, \
    x16_BUDGET, \
    x17_MONTHLY_REPORT, = xrange(18)
    xxx_OTHER                  = 999

    REPORT_CHOICES = (
        (x00_PROPOSAL,              "Proposal"),
        (x01_QUESTION_AND_ANSWER,   "Question and Answer"),
        (x02_VOLUNTEER_SITE_VISIT,  "Volunteer Site Visit"),
        (x03_PICTURES,              "Pictures"),
        (x04_AUDIT_REPORT,          "Audit Report"),
        (x05_QUARTERLY_REPORT,      "Quarterly Report"),
        (x06_ANNUAL_REPORT,         "Annual Report"),
        (x07_NEWSLETTER,            "Newsletter"),
        (x08_COMMUNICATION,         "Communication"),
        (x09_MONITORING_REPORT,     "Monitoring report"),
        (x10_PARTNERSHIP_AGREEMENT, "Partnership agreement"),
        (x11_HALF_YEARLY_REPORT,    "Half-yearly Report"),
        (x12_PROJECT_SELECTION_TEMPLATE, "Project selection template"),
        (x13_NTT,                   "Note to Trustees"),
        (x14_REJECT_DESCRIPTION,    "Rejection letter description"),
        (x15_BOARD_DECISION_MINUTES, "Board decision minutes"),
        (x16_BUDGET,                "Budget"),
        (x17_MONTHLY_REPORT,        "Monthly Report"),
        (xxx_OTHER,                 "Other"),
    )

    project     = models.ForeignKey('Project')
    show        = models.BooleanField("Display",      default=False, help_text="Display publicly: "
        "Please do not add documents that contain sensitive information such as organization bank info. "
        "Also do not display monitoring documents and partnership agreement documents publicly.")
    report_type = models.IntegerField("Report type",  choices=REPORT_CHOICES)
    desc        = models.CharField("Description",     max_length=255)
    report_file = models.FileField("Report file",     upload_to="reports")
    report_date = models.DateField("Report date",     help_text="Not the report upload date")
    upload_date = models.DateTimeField("Upload date", editable=False)
    tags        = models.ManyToManyField(Tag, blank=True)

    def can_show_report(self):
        if not self.show:
            return False

        if self.report_type in [x05_QUARTERLY_REPORT
                ,x06_ANNUAL_REPORT,x07_NEWSLETTER,
                x11_HALF_YEARLY_REPORT
                ]:
            return True
        else:
            return False

    @func_attrs(allow_tags=True, short_description='Report file')
    def show_report(self):
        filename = os.path.basename(self.report_file.name)[34:][:40]
        if not filename:
            filename = '???'
        return '<a href="%s" target="_blank">%s</a>' % (self.get_report_file_url_custom(), filename)

    class Admin:
        list_display = ('project', 'report_type', 'desc', 'show', 'show_report', 'report_date', 'upload_date')
        list_filter = ('project', )

    class Spreadsheet:
        overview = ('project', 'report_type', 'show', 'show_report', 'report_date', 'upload_date')

    '''
    Sikshana and DSS projectr reports need to be treated differently. Reports
    need to be link to the sub-projects being shown on AAP. The lists below
    contain the projects
    '''
    SIKSHANA_ID = 31
    DSS_ID = 14
    project_list = {SIKSHANA_ID: [79,83,84,86,88,89
        ],
        DSS_ID: [106,108,109,110,111,112,113,114
            ]
        }
    def save(self):
        """ If this record is being created, mark the upload time """
        if not self.id and not self.upload_date:
            self.upload_date = datetime.datetime.now()
        if not self.id:
            """Prefix the upload datetime to the filename before saving it"""
            self.report_file.name = prefixrand('reports/'+self.report_file.name)
        super(Report, self).save()

        if self.project.id in [self.SIKSHANA_ID,self.DSS_ID]:
            '''
            For Sikshana and DSS projects, created records for the AAP components
            as well
            '''
            for proj in self.project_list[self.project.id]:
                # Search to see if this has already been uploaded
                r = Report.objects.filter(project__id__exact=proj).filter(upload_date__exact=self.upload_date)
                if len(r) == 0:
                    # Add this report to the sub-project
                    project = Project.objects.get(id=proj)
                    report = Report(project=project,show=self.show,report_type=self.report_type,
                        desc=self.desc, report_file=self.report_file,report_date=self.report_date,
                        upload_date=self.upload_date)
                    report.save()

    def __unicode__(self):
        return unicode(self.project) + u": " + self.desc

    def get_report_file_url_custom(self):
        return '/project-uploads/reports/report.php?report=%s' % os.path.basename(self.report_file.name)

    def get_admin_url(self):
        return '/admin/projects/report/%d/' % self.id

#
# During the Atlanta Vibha conference, Nikhil and Lux asked for some
# extra columns to be added to the Project table. This is the SQL used
# to add these extra columns.
#
# ALTER TABLE `projects_project` MODIFY `internal_contact_id` integer NULL;
# ALTER TABLE `projects_project` ADD COLUMN `some_external_url` varchar(200) NOT NULL;
# ALTER TABLE `projects_project` ADD COLUMN `some_external_url_public` bool NOT NULL;
# ALTER TABLE `projects_project` ADD COLUMN `comments` longtext NOT NULL;
# DESC `projects_project`;
#
class Project(models.Model):
    """This is why we are doing all this.

    This is the only table that is a bit complicated. Please take time to
    patiently read what is written here.  What is here should be clear"""
    name          = models.CharField("Name",                          max_length=200)
    slug          = models.SlugField(
                    help_text="Autogenerated (by Javascript) from Name, used for URLs of project pages")
    organization  = models.ForeignKey(Organization,
                    help_text="Several projects may belong to the same organization")
    address_1     = models.CharField("Address 1",                     max_length=200)
    address_2     = models.CharField("Address 2",                     blank=True,  max_length=200)
    address_3     = models.CharField("Address 3",                     blank=True,  max_length=200)
    location      = models.ForeignKey(Location)
    beneficiaries_count = models.PositiveIntegerField("Number of beneficiaries",
                    help_text="Refers to only the DIRECT beneficiaries")
    teacher_count = models.PositiveIntegerField("Number of teachers", blank=True, null=True)
    staff_count   = models.PositiveIntegerField("Number of staff",    blank=True, null=True)
    summary       = models.CharField("Summary",                       max_length=100)
    desc          = models.TextField("Description")
    desc_html     = models.TextField("Description HTML", editable=False, blank=True, null=True)

    # The focus areas of the project
    focus_areas = models.ManyToManyField(FocusSubArea)

    # These are the project's internal and external contacts
    # internal_contact is the primary internal contact
    # internal_contacts are secondary internal contacts
    # external_contact is the primary external contact
    # external_contacts are secondary external contacts
    #
    # CAUTION: The lines below are really loooooooooong.
    #
    internal_contact  = models.ForeignKey(Volunteer,            related_name="internal_contact",  verbose_name="Project lead", blank=True, null=True)
    internal_contacts = models.ManyToManyField(Volunteer,       related_name="internal_contacts", verbose_name="Additional project leads", blank=True)
    external_contact  = models.ForeignKey(ExternalContact,      related_name="external_contact",  verbose_name="External contact",
                        help_text="The main contact person from the project")
    external_contacts = models.ManyToManyField(ExternalContact, related_name="external_contacts", verbose_name="Additional project contacts", blank=True,
                        help_text="Additional external contacts can be added here")
    modified_date     = models.DateTimeField("Modified date", editable=False, auto_now=True)

    # These are managers for adding special functionality
    objects           = models.Manager()         # The default manager, returns all projects
    current_projects  = CurrentProjectsManager() # Custom manager, returns current projects
    past_projects     = PastProjectsManager()    # Custom manager, returns past projects

    # External URL for project pictures, etc.
    some_external_url = models.URLField(verify_exists=False, blank=True, help_text="Might be used for pictures, etc.")
    some_external_url_public = models.BooleanField(default=False, help_text="Display external URL publicly?")

    # Any random comment about the project
    comments  = models.TextField("Comments",         blank=True)

    # Show this project in the "adopt a project" site
    show_adopt_project = models.BooleanField(default=False, verbose_name="Display on Adopt-a-project site?")

    # More project details that were added May 2010
    project_strategy          = models.TextField("Project Strategy", blank=True, null=True,
            help_text="In brief,  how the project is being approached")
    project_coordinator  = models.ForeignKey(ExternalContact,      related_name="project_coordinator",  verbose_name="Project Coordinator",
                        help_text="The project's coordinator or founder", blank=True, null=True)
    # This is the funding that is displayed on the webpage
    vibha_funding        = models.CharField("Vibha Funding", max_length=100, blank=True, null=True,
            help_text="Eg: $10,500 (June 2009- Feb 2010)")
    funded_component        = models.TextField("Vibha Funded Component", blank=True, null=True,
            help_text="Eg: LAFF mobile maintenance; activity materials like toys and games; hospital projects; staff salary and insurance")
    beneficiary_age        = models.CharField("Beneficiary Age", max_length=50, blank=True, null=True,
            help_text="Eg: Children 3-14 yrs")
    beneficiary_background        = models.TextField("Socio-Economic Background", blank=True, null=True,
            help_text="Eg: Municipal school students; hospitals; slums, construction sites")
    cost_per_beneficiary    = models.DecimalField("Cost per Beneficary (USD)",  max_digits=20, decimal_places=4, blank=True, null=True)

    def save(self):
        import markdown
        self.desc_html = markdown.markdown(smart_unicode(self.desc))
        super(Project, self).save()

    class Admin:
        """ This  is being ignored. The actual list is in admin.py """
        list_display = ('id3', 'name', 'show_organization', 'beneficiaries_count', 'status_string', 'summary', 'show_internal_contact', 'location')

    class Meta:
        ordering = ('name',)

    class Spreadsheet:
        additional_fields = ( 'name', 'status_string', )
        overview = ('id3', 'name', 'has_funding_details', 'status_string', 'monitoring_report_0', 'has_pictures', 'has_proposal', 'latest_report', 'internal_contact', )
        monitoring = ('id3', 'name', 'monitoring_report_0', 'monitoring_report_1', 'monitoring_report_2', 'next_monitoring_visit_due', )
        contacts = ('id3','name','show_internal_contact_info','show_organization_info',)
        overview2 = ('id3', 'name', 'status_string', 'location', 'show_project_address','beneficiaries_count', 'show_focus_areas', 'first_funding', 'funding_to_date',
                'show_organization_info', 'show_internal_contact_info', 'show_project_desc', 'show_project_picture', 'latest_report',)

    def __unicode__(self):
        return self.name

    ########################################################################
    # Project status stuff
    ########################################################################
    @func_attrs(short_description='Project Status')
    def status_string(self):
        """Returns the status of the project, as a string."""
        status = self.status()
        if status is None:
            return u"Unknown"
        else:
            return status.get_status_display()

    def status(self):
        try:
            return self.projectstatusupdate_set.latest(field_name='date')
        except ObjectDoesNotExist:
            return None

    def status_int(self):
        status = self.status()
        if status is None:
            return -1
        else:
            return status.status

    def is_current(self):
        """Returns True if this person is a current or ongoing project."""
        try:
            psu = self.projectstatusupdate_set.latest(field_name='date')
            return (psu.status == ProjectStatusUpdate.y_04_BOARD_APPROVED)
        except ObjectDoesNotExist:
            return False

    def is_past(self):
        """Returns True if this person is a completed or discontinued project."""
        try:
            psu = self.projectstatusupdate_set.latest(field_name='date')
            return ((psu.status == ProjectStatusUpdate.y_06_PAST)     or
                    (psu.status == ProjectStatusUpdate.y_07_DISCONTINUED))
        except ObjectDoesNotExist:
            return False

    def pending_action_items(self):
        return self.actionitem_set.filter(completed=False)

    def latest_funding(self):
        try:
            return self.projectfundingdetail_set.latest(field_name='end_date')
        except ObjectDoesNotExist:
            return None

    @func_attrs(short_description='First Funded')
    def first_funding(self):
        try:
            return self.projectfundingdetail_set.order_by('begin_date').latest('begin_date').begin_date
        except ObjectDoesNotExist:
            return None

    @func_attrs(short_description='Funding-to-date (USD)')
    def funding_to_date(self):
        funding = 0
        for budget in self.projectfundingdetail_set.all():
            funding += budget.budget
        return '$%0.2f'%funding
    
    # lot of functions are here
    from modellogic.project import (
        has_funding_details,
        has_pictures,
        has_proposal,
        latest_report,
        monitoring_report_0,
        monitoring_report_1,
        monitoring_report_2,
        get_relevant_reports,
        next_monitoring_visit_due,
        id3,
        get_absolute_url,
        get_factsheet_url,
        get_admin_url,
        get_gallery_url,
        get_gallery_xml_url,
        get_random_picture,
        canBeMapped,
        infoBoxCodeForMap,
        show_internal_contact_info,
        show_internal_contact_email,
        show_internal_contact_phone,
        show_organization,
        show_organization_info,
        show_project_address,
        show_focus_areas,
        show_project_desc,
        show_project_picture,
        )

# Proxy Model to display current projects
class ActiveProject(Project):
    objects  = ActiveProjectsManager() # Custom manager, returns active projects
    class Meta:
        proxy = True

# Proxy Model to display past projects
class PastProject(Project):
    objects  = PastProjectsManager() # Custom manager, returns past projects
    class Meta:
        proxy = True


class ProjectFundingDetail(models.Model):
    """Details about funding periods and the number of children benefited"""
    project     = models.ForeignKey(Project)
    begin_date  = models.DateField("Period start")
    end_date    = models.DateField("Period end")
    child_count = models.PositiveIntegerField("# Children")
    budget      = models.DecimalField("Budget approved (USD)",  max_digits=20, decimal_places=4)
    budget_inr  = models.DecimalField("Budget approved (INR)",  max_digits=20, decimal_places=4, blank=True, null=True)
    xchange_rt  = models.DecimalField("Exchange rate", max_digits=20, decimal_places=4, help_text='Exchange rate (1 USD = x INR), <a target="_blank" href="http://www.google.com/search?q=1+USD+in+INR">from google</a>')

    class Admin:
        list_display = ('project', 'begin_date', 'end_date', 'child_count', 'budget', 'xchange_rt')
        list_filter = ('begin_date', 'end_date', 'project')

    def __unicode__(self):
        # Don't know why self.budget is of type str
        # return '%s : %s : %s : %f' % (self.project, self.begin_date, self.end_date, self.budget)
        return u'%s : %s : %s : %s' % (self.project, self.begin_date, self.end_date, self.budget)

    def get_admin_url(self):
        return '/admin/projects/projectfundingdetail/%d/' % self.id

class ProjectStatusUpdate(models.Model):
    """Maintains information about updates in the status of the project"""
    y_00_RECEIVED_PROPOSAL,              \
    y_01_LEAD_ASSIGNED,                  \
    y_02_AC_APPROVED,                    \
    y_03_NATIONAL_TEAM_APPROVED,         \
    y_04_BOARD_APPROVED,                 \
    y_05_REJECTED,                       \
    y_06_PAST,                           \
    y_07_DISCONTINUED,                   = xrange(8)

    STATUS_CHOICES = (
        (y_00_RECEIVED_PROPOSAL,      "Received proposal"),
        (y_01_LEAD_ASSIGNED,          "Lead assigned"),
        (y_02_AC_APPROVED,            "AC Approved"),
        (y_03_NATIONAL_TEAM_APPROVED, "National team approved"),
        (y_04_BOARD_APPROVED,         "Ongoing"),
        (y_05_REJECTED,               "Rejected"),
        (y_06_PAST,                   "Completed"),
        (y_07_DISCONTINUED,           "Discontinued"),
    )

    z_000_NO_FCRA,                       \
    z_001_DOES_NOT_MATCH_FOCUS_AREA,     = xrange(2)
    z_999_OTHER                          = 999

    REJECT_CHOICES = (
        (z_000_NO_FCRA,                   "No FCRA"),
        (z_001_DOES_NOT_MATCH_FOCUS_AREA, "Does not match Vibha focus areas"),
        (z_999_OTHER,                     "Other"),
    )

    project = models.ForeignKey(Project)
    status  = models.IntegerField("Status",          choices=STATUS_CHOICES)
    date    = models.DateField("Status Update Date",
              help_text="The date when the status changed (not the date this entry is being made)")
    comments  = models.TextField("Comments",         blank=True, help_text=u"Like reason for rejection.")
    report  = models.ForeignKey(Report, blank=True, null=True, help_text="the relevant document for this status update")
    reject_reason = models.IntegerField("Reason for rejection", choices=REJECT_CHOICES, blank=True, null=True)

    class Admin:
        list_display = ('project', 'status', 'date')
        list_filter = ('project', 'status')

    def __unicode__(self):
        return unicode(self.project) + u": " + unicode(self.status) + u": " + str(self.date)

    def notify(self):
        """Notify concerned people when a new status is added."""
        project = self.project
        if (project.internal_contact is not None) and (project.internal_contact.contact is not None):
            lead = project.internal_contact.contact
            recipients = [ lead.email, 'lux@vibha.org' ]
        else:
            lead = None
            recipients = [ 'lux@vibha.org' ]
        organization = project.organization
        sender = 'Vibha Projects <projects@vibha.org>'
        subject = 'Project status changed: %s' % self.project
        msg = render_to_string('projects/status-change-notification.txt', {
            'project': project,
            'organization': organization,
            'status': self,
            'lead': lead,})
        send_mail(subject, msg, sender, recipients, fail_silently=False)

    def save(self):
        super(ProjectStatusUpdate, self).save()
        self.notify()


class Disbursal(models.Model):
    project        = models.ForeignKey(Project)
    amount         = models.DecimalField("Amount (USD)",    max_digits=20, decimal_places=2)
    amount_inr     = models.DecimalField("Amount (INR)",  max_digits=20, decimal_places=4, blank=True, null=True)
    exchange_rate  = models.DecimalField("Exchange rate",   max_digits=20, decimal_places=3, help_text='Exchange rate (1 USD = x INR), <a target="_blank" href="http://www.google.com/search?q=1+USD+in+INR">from google</a>')
    scheduled_date = models.DateField("Scheduled date")
    disbursed_date = models.DateField("Disbursed date",                blank=True, null=True, help_text="to be entered by the Vibha office; project leads, leave this entry blank")
    comments       = models.TextField("Comments",  blank=True)
    notification_sent = models.BooleanField("Notification Sent", default=False, help_text="Has a notification email been sent")

    def get_admin_url(self):
        return '/admin/projects/disbursal/%d/' % self.id

    class Admin:
        list_display = ('project', 'amount', 'scheduled_date', 'disbursed_date')
        list_filter = ('scheduled_date', 'disbursed_date', 'project')

    def __unicode__(self):
        return unicode(self.project) + u": " + unicode(self.amount) + u": " + unicode(self.scheduled_date) + u": " + unicode(self.disbursed_date)

    def notify(self):
        """Notify concerned people when a disbursal is made."""
        project = self.project
        lead = project.internal_contact.contact
        organization = project.organization
        sender = 'Vibha Office <office@vibha.org>'
        recipients = [ 'office@vibha.org', lead.email, 'suriya@vibha.org' ]
        subject = 'Disbursal made : %s' % self.project
        msg = render_to_string('projects/disbursal-notification.txt', {
            'project': project,
            'organization': organization,
            'disbursal': self,
            'lead': lead,})
        send_mail(subject, msg, sender, recipients, fail_silently=False)

        # Send notification email to organization contact
        recipients = [ 'office@vibha.org', 'amenon81+vibha@gmail.com', lead.email, organization.email ]
        msg = render_to_string('projects/disbursal-notification-external-contact.txt', {
            'organization': organization,
            'disbursal': self,
            })
        send_mail(subject, msg, sender, recipients, fail_silently=False)

        self.notification_sent = True
        self.save()

    def save(self):
        super(Disbursal, self).save()
        if self.disbursed_date is not None and not self.notification_sent:
            self.notify()

from vibha.utils.shortcuts import prefixrand

class Picture(models.Model):
    project     = models.ForeignKey(Project)
    show        = models.BooleanField("Display",              default=False, help_text="Display publicly")
    desc        = models.TextField("Description", help_text="please add as much information as you can here :)")
    # image
    image       = models.ImageField("Picture file",           upload_to="pictures",
                                     width_field="width",     height_field="height")
    width       = models.PositiveIntegerField("Image width",  editable=False, null=True)
    height      = models.PositiveIntegerField("Image height", editable=False, null=True)
    # thumbnail
    thumbnail   = models.ImageField("Thumbnail",              upload_to="thumbs",
                                     width_field="thwidth",   height_field="thheight",
                                     editable=False,          null=True)
    thwidth     = models.PositiveIntegerField("Thumbnail width",  editable=False, null=True)
    thheight    = models.PositiveIntegerField("Thumbnail height", editable=False, null=True)
    copyrighted = models.BooleanField("Copyrighted")
    date        = models.DateField("Picture date",            help_text="Not the picture upload date")
    upload_date = models.DateTimeField("Upload date",         editable=False, auto_now_add=True)
    tags        = models.ManyToManyField(Tag, blank=True)
    
    # medium sized image
    medthumb = models.ImageField("Medium Thumbnail", upload_to="medthumbs", null=True, max_length=200)

    @func_attrs(allow_tags=True, short_description='Image')
    def show_thumb(self):
        if self.image and self.image.name is not None:
            return '<a href="%s" target="_blank"><img src="%s"></a>' % (self.image.url, self.thumbnail.url)
        else:
            return 'No Image'

    class Admin:
        list_display = ('project', 'desc', 'show', 'show_thumb', 'copyrighted', 'date')
        list_filter = ('project', )

    def save(self):
        """Prefix the upload datetime to the filename before saving it. In addition, create a thumbnail after saving this image"""
        self.image.name = prefixrand(self.image.name)
        super(Picture, self).save()
        # Create thumbnail
        if self.image and not self.thumbnail:
            import Image
            from django.core.files.base import ContentFile 
            img = Image.open(self.image.path)
            img.thumbnail((128, 128), Image.ANTIALIAS)
            fp = StringIO()
            img.save(fp, "JPEG")
            th_filename = 'thumbs/'+os.path.basename(self.image.path)
            self.thumbnail.storage.save(th_filename,ContentFile(fp.getvalue()))
            self.thumbnail.name = th_filename
            super(Picture, self).save()
        # Create medium-sized thumbnail
        if self.image and not self.medthumb:
            import Image
            from django.core.files.base import ContentFile 
            img = Image.open(self.image.path)
            img.thumbnail((640, 480), Image.ANTIALIAS)
            fp = StringIO()
            img.save(fp, "JPEG")
            th_filename = 'medthumbs/'+os.path.basename(self.image.path)
            self.medthumb.storage.save(th_filename,ContentFile(fp.getvalue()))
            self.medthumb.name = th_filename
            super(Picture, self).save()

    def __unicode__(self):
        return unicode(self.project) + u": " + self.desc

class ActionItem(models.Model):
    t_00_PROJECT_HAS_NO_STATUS,                   \
    t_01_PROJECT_HAS_NO_LEAD,                     \
    t_02_PROJECT_PROCESS_IDLE_FOR_LONG,           \
    t_03_REJECTED_PROJECT_NEEDS_REJECTION_LETTER, \
    t_04_PROJECT_AWAITS_RENEWAL,                  \
    t_05_PROJECT_DOES_NOT_HAVE_BOARD_MINUTES,     \
    t_06_PROJECT_VISIT_DID_NOT_HAPPEN,            \
    t_07_SELECTION_TEMPLATE_NOT_PRESENT,          \
    t_08_NATIONAL_TEAM_APPROVED_BUT_NEEDS_INFO,   \
    t_09_NEEDS_HALF_YEARLY_REPORT,                \
    t_10_PROJECT_UNDECIDED_FOR_LONG,              \
    t_11_PROJECT_VISIT_COMING_UP,                 \
    t_12_PROJECT_AWAITS_RENEWAL_GENTLE,           \
    t_13_ANNUAL_REPORT_DUE,                       \
    t_14_ANNUAL_REPORT_DUE_GENTLE                 = xrange(15)

    ACTION_ITEM_TYPE_CHOICES = (
        (t_00_PROJECT_HAS_NO_STATUS,                   "Project has no status"),
        (t_01_PROJECT_HAS_NO_LEAD,                     "Project has no lead"),
        (t_02_PROJECT_PROCESS_IDLE_FOR_LONG,           "Project process idle for long"),
        (t_03_REJECTED_PROJECT_NEEDS_REJECTION_LETTER, "Reject project needs rejection letter"),
        (t_04_PROJECT_AWAITS_RENEWAL,                  "Project awaits renewal"),
        (t_05_PROJECT_DOES_NOT_HAVE_BOARD_MINUTES,     "Project does not have board minutes"),
        (t_06_PROJECT_VISIT_DID_NOT_HAPPEN,            "Project visit did not happen"),
        (t_07_SELECTION_TEMPLATE_NOT_PRESENT,          "Selection template not present"),
        (t_08_NATIONAL_TEAM_APPROVED_BUT_NEEDS_INFO,   "National team approved but needs info"),
        (t_09_NEEDS_HALF_YEARLY_REPORT,                "Project needs half-yearly report"),
        (t_10_PROJECT_UNDECIDED_FOR_LONG,              "Project undecided for long"),
        (t_11_PROJECT_VISIT_COMING_UP,                 "Project visit is coming up soon"),
        (t_12_PROJECT_AWAITS_RENEWAL_GENTLE,           "Project awaits renewal"),
        (t_13_ANNUAL_REPORT_DUE,                       "Project final report is due"),
        (t_14_ANNUAL_REPORT_DUE_GENTLE,                "Project final report is due soon"),
    )
    project     = models.ForeignKey(Project, blank=True, null=True)
    desc        = models.TextField("Description", help_text="please add as much information as you can here :)")
    due_date    = models.DateField("Due date")
    completed_date    = models.DateField("Completed date", null=True,blank=True)
    owner       = models.ForeignKey(Volunteer)
    ai_type     = models.IntegerField("ActionItem type", choices=ACTION_ITEM_TYPE_CHOICES)
    completed   = models.BooleanField(default=False)
    stop_email  = models.BooleanField("Stop Emails",help_text="Stop sending emails for this action item",default=False)

    def get_admin_url(self):
        return '/admin/projects/actionitem/%d/' % self.id

    def __unicode__(self):
        return self.desc

    def save(self):
        if not self.completed_date and self.completed:
            self.completed_date = datetime.date.today()
        super(ActionItem, self).save()

    class Admin:
        list_display = ('project', 'desc', 'due_date', 'owner', 'ai_type', 'completed', )
        list_filter = ('ai_type', 'project', )

class ProjectVisit(models.Model):
    project        = models.ForeignKey(Project)
    visitor        = models.ForeignKey(Volunteer, blank=True, null=True)
    scheduled_date = models.DateField()
    visit_date     = models.DateField(blank=True, null=True, help_text="to be entered when visit happens; initally, leave this entry blank")
    report         = models.ForeignKey(Report, blank=True, null=True, help_text="the visit report for this project")
    comments       = models.TextField(blank=True)

    def __unicode__(self):
        return unicode(self.project) + u": " + unicode(self.scheduled_date) + u": " + unicode(self.visit_date)

# vim:tw=150:nowrap:ts=4:sw=4:et:
