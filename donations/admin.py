
from django.contrib import admin
from vibha.donations.models import Company, Donation, HTGSignup

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'vibha_id', 'first_name_coord', 'last_name_coord', 'phone', 'email')
    list_filter = ('is_active',)

class DonationAdmin(admin.ModelAdmin):
    list_display = ('signup_date', 'first_name', 'last_name', 'email', 'phone', 'amount', 'referrer', 'action_center', 'show_trans_status', 'show_adopt_a_project',)
    list_filter = ('action_center',)

class HTGSignupAdmin(admin.ModelAdmin):
    list_display = ('signup_date', 'first_name', 'last_name', 'email',
            'phone', 'use_check', 'state')

admin.site.register(Company, CompanyAdmin)
admin.site.register(Donation, DonationAdmin)
admin.site.register(HTGSignup, HTGSignupAdmin)
