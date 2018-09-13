
import urllib
from django.db import models

class TriviaGuruRegistration(models.Model):
    signup_date       = models.DateTimeField("Signup date",        editable=False, auto_now=True)
    team_name         = models.CharField("Team name",              max_length=100)
    captain_name      = models.CharField("Captain name",           max_length=100)
    captain_email     = models.EmailField("Captain E-mail")
    captain_phone     = models.CharField("Captain Phone",          max_length=100)
    member2_name      = models.CharField("Member 2 name",          max_length=100)
    member3_name      = models.CharField("Member 3 name",          max_length=100)
    num_students      = models.IntegerField("Num students",        blank=True, null=True)
    num_non_students  = models.IntegerField("Num non-students",    blank=True, null=True)
    comments          = models.TextField("Comments",               blank=True)
    paid              = models.NullBooleanField("Paid fee?",           default=False, null=True, blank=True)

    def paypal_redirect_url(self):
        return '/triviaguru/pay/%d/' % self.id

    def paypal_url(self):
        num_students = max(0, self.num_students)
        num_non_students = max(0, self.num_non_students)
        if (num_students + num_non_students <= 0):
            num_non_students = 1
        amount = (num_students * 10) + (num_non_students * 15)
        query = [
            ('cmd', '_xclick'),
            ('business', 'ramdas@vibha.org'),
            ('item_name', 'Vibha Austin Trivia Guru 2009'),
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
        return self.captain_name

    def emailRecipients(self):
        return [ self.captain_email, 'info@austin.vibha.org', ]
