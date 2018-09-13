# from django.test.client import Client
# c = Client()
# CAPTCHA_URL = '/captcha/'
# CFC_URL = '/cfc/new/'
# 
# # Get the id number for Texas
# from vibha.projects.models import State
# texas = State.objects.get(name='Texas')
# 
# # Get the captcha
# c.get(CAPTCHA_URL)
# session = c.session._session
# captcha = session['vibha.utils.captcha.captcha_solutions'][0]
# 
# # Fill the cfc form
# c.get(CFC_URL)
# post_dict = {
#  'email':       'suriya@gmail.com',
#  'first_name':  'Suriya',
#  'last_name':   'Subramanian',
#  'address_1':   '3543 Greystone Dr #1054',
#  'city':        'Austin',
#  'zipcode':     '78731',
#  'state':       unicode(texas.id),
#  'phone':       '512-342-9622',
#  'location':    'Austin1',
#  'receipt':     True,
#  'agreement':   True,
#  'captcha':     captcha,
# }
