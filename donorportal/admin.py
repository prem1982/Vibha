from django.contrib import admin
from vibha.donorportal.models import Campaign,Cart,Message,Donation,WatchProject

admin.site.register(Campaign)
admin.site.register(Cart)
admin.site.register(Message)

class DonationAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'project', 'campaign','amount',)
    list_filter = ('project',)

admin.site.register(Donation, DonationAdmin)
admin.site.register(WatchProject)
