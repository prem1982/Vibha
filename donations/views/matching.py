
# $Id: matching.py 326 2007-04-23 03:05:13Z suriya $

# Views related to matching donations

from django.http import HttpResponse
from vibha.donations.models import Company
from django.template.defaultfilters import escape
from django.shortcuts import render_to_response
import re

def _highlight_search(name, search):
    """
    Highlight the searched string in name.
    """
    search = escape(search)
    name = escape(name)
    p = re.compile(r'(%s)' % search, re.IGNORECASE)
    return p.sub(r'<strong>\1</strong>', name)

def ajax_companies_list_response(request):
    """
    List of companies for autocompletion, in the format expected by
    http://wiki.script.aculo.us/scriptaculous/show/Ajax.Autocompleter
    """
    if request.POST:
        search = request.POST.get('search', '')
        matches = Company.objects.filter(name__icontains=search)
    else:
        matches = []
    code = ''.join('<li id="%d">%s</li>' % (i.id, _highlight_search(i.name, search)) for i in matches)
    return HttpResponse('<ul>%s</ul>' % code)

def company_list(request):
    companieS = Company.objects.filter(is_active=True).order_by('name')
    return render_to_response('donations/matching.dmpl',
            {
                'companieS': companieS,
                })

