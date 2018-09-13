
from django.contrib import admin
from vibha.austinchampion.models import Champion

class ChampionAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'fundraising_page_url', 'donation_page_url')
    prepopulated_fields = {'slug': ('first_name', 'last_name',)}

admin.site.register(Champion, ChampionAdmin)
