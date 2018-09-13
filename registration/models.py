from django.db import models
from django.contrib.auth.models import User
from vibha.registration.countries import LIST_OF_COUNTRIES
from django.contrib.localflavor.us.models  import USStateField

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True,)
    address1 = models.CharField(max_length=100,verbose_name='Street Address',blank=True,null=True)
    address2 = models.CharField(max_length=100,blank=True,null=True)
    company_name = models.CharField(max_length=100,blank=True,null=True)
    phone_number = models.CharField(max_length=20,blank=True,null=True)
    city = models.CharField(max_length=100,blank=True,null=True)
    state = models.CharField(max_length=100,blank=True,null=True)
    zipcode = models.CharField(max_length=20,blank=True,null=True)
    country = models.CharField(choices=LIST_OF_COUNTRIES,max_length=8,blank=True,null=True)
    send_project_mails = models.BooleanField(default=True)
    send_event_mails = models.BooleanField(default=True)
    public_profile = models.URLField(verbose_name='Public Profile link',blank=True,null=True,help_text='You may link to your profile on Facebook, Twitter or other internet homepage, to help others identify you.')
    
    @models.permalink
    def get_absolute_url(self):
        return ('profiles_profile_detail', (), { 'username': self.user.username })

    def __unicode__(self):
        return u"Registration information for %s" % self.user
    
    

