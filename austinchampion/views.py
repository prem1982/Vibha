# Create your views here.

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from vibha.austinchampion.models import Champion

def fundraiser(request, slug):
    champion = get_object_or_404(Champion, slug=slug)
    donations = champion.donation_set.all()
    return render_to_response('austinchampion/fundraiser.html',
            {'champion': champion,
             'donations': donations,})

def welcome(request):
    champion = get_object_or_404(Champion, slug='vibha-austin')
    champions = Champion.objects.order_by('first_name')
    list_of_donations = [ c.donation_set.all() for c in champions ]
    return render_to_response('austinchampion/welcome.html',
            {'champion': champion,
             'champions': champions,
             'list_of_donations': list_of_donations, })
