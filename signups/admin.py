
from django.contrib import admin
from vibha.signups.models import Contact

class ContactAdmin(admin.ModelAdmin):
    list_display = ('signup_date','last_name', 'first_name', 'location', )
    list_filter = ('location', )


admin.site.register(Contact,ContactAdmin)
