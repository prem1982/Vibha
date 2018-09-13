
from django.db import models
from vibha.projects.models import State, ActionCenter

# Create your models here.

class CFCSignup(models.Model):
    signup_date    = models.DateTimeField("Signup date",  editable=False, auto_now=True)
    # The jar ID
    jarid          = models.CharField("Jar #",                      max_length=100, blank=True)
    first_name     = models.CharField("First Name",                 max_length=100, blank=False)
    last_name      = models.CharField("Last Name",                  max_length=100, blank=False)
    pg_first_name  = models.CharField("Parent/Guardian First Name", max_length=100, blank=True)
    pg_last_name   = models.CharField("Parent/Guardian Last Name",  max_length=100, blank=True)
    email          = models.EmailField("E-mail",                                   blank=False)
    phone          = models.CharField("Phone",                      max_length=100, blank=False)
    address_1      = models.CharField("Address Line1",              max_length=100, blank=True)
    address_2      = models.CharField("Address Line2",              max_length=100, blank=True)
    city	       = models.CharField("City",                       max_length=100, blank=True)
    state          = models.ForeignKey(State,                       blank=True, null=True)
    actioncenter   = models.ForeignKey(ActionCenter,                blank=True, null=True)
    zipcode        = models.CharField("ZIP",                        max_length=100, blank=True)
    comments       = models.TextField("Comments",                                  blank=True)
    receipt        = models.BooleanField("Need receipt?", default=False)
    agreement      = models.BooleanField("Agreement",     default=False)

    def emailRecipients(self):
        return [ 'cfc@vibha.org', self.email ]

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)
