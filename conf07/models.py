# $Id: models.py 468 2008-05-22 07:38:05Z suriya $

from django.db import models

# conference signup model
class Signup(models.Model):
    signup_date    = models.DateTimeField("Signup date",  editable=False, auto_now=True)
    first_name     = models.CharField("* First name",        max_length=100)
    middle_name    = models.CharField("Middle name",         max_length=100, blank=True)
    last_name      = models.CharField("* Last name",         max_length=100)
    ac             = models.CharField("* Action Center or Location",  max_length=100)
    email          = models.EmailField("* E-mail")
    accomodation   = models.NullBooleanField("Accomodation requested?", blank=True, null=True)
    guests         = models.TextField("Additional guests (provide names)",          blank=True)
    pickup         = models.NullBooleanField("Airline pickup requested?", blank=True, null=True)
    transportation = models.NullBooleanField("Venue transportation requested?", blank=True, null=True)
    requests       = models.TextField("Other requests",         blank=True)
    volunteer      = models.NullBooleanField("Would you like to volunteer?", blank=True, null=True)
    webcast_viewing = models.NullBooleanField("Viewing the webcast?", blank=True, null=True, default=False)

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

    def emailRecipients(self):
        return [ self.email, 'vconference@vibha.org' ]

# vim:tw=150:nowrap:ts=4:sw=4:et:
