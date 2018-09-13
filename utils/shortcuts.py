
# $Id: shortcuts.py 460 2008-04-02 22:18:42Z suriya $

# Some useful functions

from django.conf import settings
from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404
from vibha.projects.models import Country, ActionCenter, State
from django.db.models import Q
from md5 import md5
import re
import os
import stat
from datetime import datetime
import shutil
from StringIO import StringIO

__all__ = ('our_flatpage',
           'accepts_cookies',
           'is_in_US',
           'states_in_the_US',
           'states_in_the_US_and_other',
           'vibha_action_centers',
           'get_object_or_none',
           'prefixrand')

def our_flatpage(content):
    """Return content in Vibha's template"""
    return render_to_response('flatpage.html', {'content': content, 'title':   'Vibha',})

PREFIX = 'vibha.utils.shortcuts.'
ACCEPTS_COOKIES = PREFIX + 'accepts_cookies'
def accepts_cookies(request):
    """Checks whether a browser accepts cookies.

    http://www.djangoproject.com/documentation/sessions/#setting-test-cookies
    """
    if request.session.get(ACCEPTS_COOKIES, False):
        return True
    elif request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        request.session[ACCEPTS_COOKIES] = True
        return True
    else:
        request.session.set_test_cookie()
        return False

def is_in_US(state):
    """Is this state in the US?"""
    return (state.country.id == 2)

def states_in_the_US():
    """Returns a queryset"""
    return Country.objects.get(id=2).state_set.all()

def states_in_the_US_and_other():
    """The states in the US and "Other"."""
    return State.objects.filter(Q(country__id=2) | Q(country__id=3))

def vibha_action_centers():
    """Returns a queryset"""
    return ActionCenter.objects.all()

def get_object_or_none(klass, *args, **kwargs):
    try:
        return get_object_or_404(klass, *args, **kwargs)
    except Http404:
        return None

def prefixrand(filename):
    """Prefix file names with a random string to make it unique. This
    ensures people do not have to worry about filenames."""
    # Django has a bug #639
    # http://code.djangoproject.com/ticket/639
    # Because of this, the save() method is called multiple times for FileFields and ImageFields
    # As a result of this, we will prefix the date several times.
    # The check below avoids this
    if filename and not re.match(r'r[a-f0-9]{32}-', os.path.basename(filename)):
        pathname,basename = os.path.split(filename)
        h = md5()
        h.update(unicode(datetime.now()))
        h.update(basename)
        new_basename = 'r%s-%s' % (h.hexdigest(), basename)
        new_filename = os.path.join(pathname, new_basename)
        new_location = os.path.join(settings.MEDIA_ROOT, new_filename)
        old_location = os.path.join(settings.MEDIA_ROOT, filename)
        #shutil.move(old_location, new_location)
        return new_filename
    else:
        return filename

def removeprefix(filename, write = False):
    """Remove previously prefixed files. This is the first step
    in renaming these files."""
    if filename and re.match(r'r[a-f0-9]{32}-', os.path.basename(filename)):
        pathname,basename = os.path.split(filename)
        # Remove the old hash from the filename
        basename = re.search(r'(?<=-).*', os.path.basename(filename)).group(0)

        new_filename = os.path.join(pathname, basename)
        new_location = os.path.join(settings.MEDIA_ROOT, new_filename)
        old_location = os.path.join(settings.MEDIA_ROOT, filename)
        if write:
            shutil.move(old_location, new_location)
        return new_filename
    else:
        return filename

