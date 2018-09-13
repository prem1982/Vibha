
# $Id: __init__.py 406 2007-12-03 02:38:44Z suriya $

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required

from vibha.donations.models import Donation

@staff_member_required
def echo_response(request, id):
    donation = get_object_or_404(Donation, id=id)
    return HttpResponse(donation.trans_response)
