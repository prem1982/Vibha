
from django.contrib import admin
from vibha.cfc.models import CFCSignup

class CFCSignupAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone')

admin.site.register(CFCSignup, CFCSignupAdmin)
