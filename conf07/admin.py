
from django.contrib import admin
from vibha.conf07.models import Signup

class SignupAdmin(admin.ModelAdmin):
    list_display = ('signup_date', 'first_name', 'last_name', 'ac','email','webcast_viewing')
    list_filter = ('signup_date','pickup','accomodation','webcast_viewing')

admin.site.register(Signup, SignupAdmin)
