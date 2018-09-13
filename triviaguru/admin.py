
from django.contrib import admin
from vibha.triviaguru.models import TriviaGuruRegistration

class TriviaGuruRegistrationAdmin(admin.ModelAdmin):
    list_display = ('signup_date', 'captain_name', 'captain_email',
            'captain_phone', 'team_name', 'num_students',
            'num_non_students', 'paid', 'comments', )

admin.site.register(TriviaGuruRegistration, TriviaGuruRegistrationAdmin)
