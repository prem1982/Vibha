
from django.contrib import admin
from vibha.austincricket08.models import AustinCricket08Registration

class AustinCricket08RegistrationAdmin(admin.ModelAdmin):
    list_display = ('signup_date', 'captain_first_name',
            'captain_last_name', 'captain_email', 'captain_phone',
            'team_name', 'num_students', 'num_non_students', 'paid',
            'comments', )

admin.site.register(AustinCricket08Registration, AustinCricket08RegistrationAdmin)
