
# $Id: dates.py 367 2007-06-18 20:22:02Z suriya $

from django.utils import dates as djangodates
from datetime import date
TODAY = date.today()

MONTH_CHOICES = tuple((k, v) for k, v in djangodates.MONTHS.iteritems())

def newer(date1, date2):
    return (date1 > date2)

def older(date1, date2):
    return (date1 < date2)

def in_the_past(date1):
    return newer(TODAY, date1)

def in_the_future(date1):
    return older(TODAY, date1)

def days_from(date1):
    return (TODAY - date1).days

def days_to(date1):
    return (date1 - TODAY).days
