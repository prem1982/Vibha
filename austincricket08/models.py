from django.db import models

import urllib

# Create your models here.

class AustinCricket08Registration(models.Model):
    signup_date         = models.DateTimeField("Signup date",        editable=False, auto_now=True)
    captain_first_name  = models.CharField("Captain First name",     max_length=100)
    captain_last_name   = models.CharField("Captain Last name",      max_length=100)
    captain_email       = models.EmailField("Captain E-mail")
    captain_phone       = models.CharField("Captain Phone",          max_length=100)
    individual          = models.BooleanField("Individual or Team",  default=False)
    team_name           = models.CharField("Team name",              max_length=100, blank=True)
    num_students        = models.IntegerField("Num students",        blank=True, null=True)
    num_non_students    = models.IntegerField("Num non-students",    blank=True, null=True)
    comments            = models.TextField("Comments",               blank=True)
    paid                = models.NullBooleanField("Paid fee?",           default=False, null=True, blank=True)

    def paypal_redirect_url(self):
        return '/austincricket/pay/%d/' % self.id

    def paypal_url(self):
        if self.individual:
            num_students = max(0, self.num_students)
            num_non_students = max(0, self.num_non_students)
            if (num_students + num_non_students <= 0):
                num_non_students = 1
        else:
            num_students = max(0, self.num_students)
            num_non_students = max(0, self.num_non_students)
            if (num_students + num_non_students < 8):
                num_non_students += (8 - (num_students + num_non_students))
        amount = (num_students * 15) + (num_non_students * 20)
        query = [
            ('cmd', '_xclick'),
            ('business', 'ramdas@vibha.org'),
            ('item_name', 'Vibha Austin Cricket 2011'),
            ('item_number', self.id),
            ('amount', amount),
            ('page_style', 'Vibha'),
            ('no_shipping', '1'),
            ('return', 'http://www.vibha.org'),
            ('cancel_return', 'http://www.vibha.org'),
            ('cn', self.team_name),
            ('currency_code', 'USD'),
            ('lc', 'US'),
            ('bn', 'PP-BuyNowBF'),
            ('charset', 'UTF-8'),
        ]

        return ('https://www.paypal.com/cgi-bin/webscr?%s' % urllib.urlencode(query))

    def __unicode__(self):
        return '%s %s' % (self.captain_first_name, self.captain_last_name)

    def emailRecipients(self):
        return [ self.captain_email, 'cricket@austin.vibha.org', 'smitanaik@gmail.com' ]


    class Spreadsheet:
        additional_fields = ()
        contacts = ('captain_first_name',
                'captain_last_name', 'captain_email', 'captain_phone',
                'team_name', )
