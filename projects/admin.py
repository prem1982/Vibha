
from django.contrib import admin
from vibha.projects.models import (Country, State, ActionCenter, FocusArea,
        FocusSubArea, Contact, Volunteer, ExternalContact, Location,
        Organization, Tag, Report, Project, ActiveProject, PastProject, 
        ProjectFundingDetail, ProjectStatusUpdate, Disbursal, Picture, 
        ActionItem, ProjectVisit)

class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', )

class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'postal', 'country')

class ActionCenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')

class FocusSubAreaAdmin(admin.ModelAdmin):
    list_display = ('focus', 'name')

class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone')

class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('contact', 'action_center')

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'type', 'latitude', 'longitude', )

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'contact','email','phone')
    filter_horizontal = ('focus_areas',)
    fieldsets = (
        (None,               {'fields':  ('name', 'url')}),
        ('Contact person',   {'fields':  ('contact', 'contact_title'),
                              'classes': ['collapse wide']}),
        ('Email/Phone/Fax',  {'fields':  ('email', 'alt_email', 'phone', 'alt_phone', 'fax'),
                              'classes': ['collapse wide']}),
        ('Address',          {'fields':  ('address_1', 'address_2', 'address_3', 'city', 'state', 'zipcode'),
                              'classes': ['collapse wide']}),
        ('Bank information', {'fields':  ('bank_name', 'bank_address', 'bank_ac_name', 'bank_ac_num', 'bank_phone', 'bank_xfer'),
                              'classes': ['collapse wide']}),
        ('Tax information',  {'fields':  ('tax_id', 'fcra', 'fcra_status', 'soc_reg'),
                              'classes': ['collapse wide']}),
        ('Focus areas',      {'fields':  ('focus_areas',),
                              'classes': ['collapse wide']}),
    )

class ReportAdmin(admin.ModelAdmin):
    list_display = ('project', 'report_type', 'desc', 'show', 'show_report', 'report_date', 'upload_date')
    list_filter = ('show', 'report_type', 'project')
    filter_horizontal = ('tags',)

class InlinePictures(admin.TabularInline):
    model = Picture
    extra = 0
    fields = ('date', 'copyrighted')

class InlineDisbursals(admin.TabularInline):
    model = Disbursal
    extra = 0
    fields = ('amount', 'scheduled_date', 'disbursed_date')

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id3', 'name', 'show_organization', 'beneficiaries_count', 'status_string', 'summary', 'internal_contact', 'show_internal_contact_email', 'show_internal_contact_phone', 'location')
    prepopulated_fields = {'slug': ('name',)}

    list_filter = ('show_adopt_project','focus_areas')
    filter_horizontal = ('focus_areas', 'internal_contacts', 'external_contacts')
    fieldsets = (
        (None,                 {'fields':  ('name', 'slug', 'organization')}),
        ('Address',            {'fields':  ('address_1', 'address_2', 'address_3', 'location'),
                                'classes': ['collapse wide']}),
        ('People',             {'fields':  ('internal_contact', 'internal_contacts', 'external_contact', 'external_contacts', 'project_coordinator'),
                                'classes': ['collapse wide']}),
        ('Main Information',   {'fields':  ('beneficiaries_count', 'teacher_count', 'staff_count', 'summary', 'project_strategy', 'desc', 'beneficiary_age', 'beneficiary_background','vibha_funding','funded_component','cost_per_beneficiary'),
                                'classes': ['collapse wide']}),
        ('Picture URLs',       {'fields':  ('some_external_url', 'some_external_url_public'),
                                'classes': ['collapse wide']}),
        (None,                 {'fields':  ('focus_areas', 'comments','show_adopt_project')}),
    )
#     inlines = [InlinePictures, InlineDisbursals]
    search_fields = ['name']

class ProjectFundingDetailAdmin(admin.ModelAdmin):
    list_display = ('project', 'begin_date', 'end_date', 'child_count', 'budget', 'xchange_rt','budget_inr')
    list_filter = ('begin_date', 'end_date', 'project')

class ProjectStatusUpdateAdmin(admin.ModelAdmin):
    list_display = ('project', 'status', 'date')
    list_filter = ('project', 'status')

class DisbursalAdmin(admin.ModelAdmin):
    list_display = ('project', 'amount', 'scheduled_date', 'disbursed_date')
    list_filter = ('scheduled_date', 'disbursed_date', 'project')

class PictureAdmin(admin.ModelAdmin):
    list_display = ('project', 'desc', 'show', 'show_thumb', 'copyrighted', 'date')
    list_filter = ('project', )
    filter_horizontal = ('tags',)

class ActionItemAdmin(admin.ModelAdmin):
    list_display = ('project', 'desc', 'due_date', 'completed_date', 'owner', 'ai_type',
            'completed', 'stop_email', )
    list_filter = ('ai_type', 'project', )

class ProjectVisitAdmin(admin.ModelAdmin):
    list_display = ('project', 'visitor', 'scheduled_date', 'visit_date', 'report')

admin.site.register(ActionCenter, ActionCenterAdmin)
admin.site.register(ActionItem, ActionItemAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Disbursal, DisbursalAdmin)
admin.site.register(ExternalContact)
admin.site.register(FocusArea)
admin.site.register(FocusSubArea, FocusSubAreaAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Picture, PictureAdmin)
admin.site.register(ProjectFundingDetail, ProjectFundingDetailAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ActiveProject, ProjectAdmin)
admin.site.register(PastProject, ProjectAdmin)
admin.site.register(ProjectStatusUpdate, ProjectStatusUpdateAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Tag)
admin.site.register(Volunteer, VolunteerAdmin)
admin.site.register(ProjectVisit, ProjectVisitAdmin)
