from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Volunteer(models.Model):
	datecreated = models.DateTimeField()
	volposition = models.CharField(max_length=300)
	roledesc    = models.CharField(max_length=5000)
	timeyear	= models.IntegerField(choices=YEAR_CHOICES)
	timemonth   = models.IntegerField(
	Qualreqt    = models.CharField(max_length=8000)
	Duration    = models.

class Bookmark(models.Model):
	title = models.CharField(max_length=200)
	user  = models.ForeignKey(User)
	link  = models.ForeignKey(Link)