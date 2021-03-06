from django.db import models

# Create your models here.

class Champion(models.Model):
    first_name    = models.CharField(max_length=100)
    last_name     = models.CharField(max_length=100)
    email         = models.EmailField()
    goal          = models.DecimalField(max_digits=9, decimal_places=2)
    message       = models.TextField(blank=True)
    slug          = models.SlugField(
                    help_text="Autogenerated (by Javascript) from First name")

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

    def donation_page_url(self):
        return 'https://secure.vibha.org/dreammile/austin/%s/donate/' % self.slug

    def fundraising_page_url(self):
        return 'https://secure.vibha.org/dreammile/austin/%s/' % self.slug
