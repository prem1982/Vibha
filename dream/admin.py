
from django.contrib import admin
from vibha.dream.models import Event

class EventAdmin(admin.ModelAdmin):
    list_display = ('honoree_first_name', 'honoree_last_name', 'email', 'short_title', 'event_date', 'show_thumb', 'get_absolute_url', 'donation_page_url')
    prepopulated_fields = {'slug': ('honoree_first_name', 'short_title')}

admin.site.register(Event, EventAdmin)
