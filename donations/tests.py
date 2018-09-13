
# $Id: tests.py 424 2008-01-12 01:01:40Z suriya $

"""
>>> from vibha.utils.BeautifulSoup import BeautifulSoup

# Initialize the database
>>> from django.core import management
>>> management.call_command('loaddata', 'test_initial_data_country.json', 'test_initial_data_state.json', 'test_initial_data_company.json', verbosity=0)

# Get the id number for Texas
>>> from vibha.projects.models import State
>>> texas = State.objects.get(name='Texas')

# Get the id number for Microsoft
>>> from vibha.donations.models import Company
>>> microsoft = Company.objects.get(name='Microsoft')

# Before we start, check that we have no donations yet
>>> from vibha.donations.models import Donation
>>> print Donation.objects.all()
[]

>>> from django.test.client import Client
>>> c = Client()
>>> CAPTCHA_URL = '/utils/captcha/'
>>> DONATE_URL = '/donations/single/new/'

# Check that we return correct information for the autocomplete Ajax
# textbox
>>> print c.post('/ajax/companies/', {'search': 'mic'}).content
<ul><li id="105"><strong>Mic</strong>rosoft</li><li id="52">National Se<strong>mic</strong>onductor</li><li id="114">Sun <strong>Mic</strong>roSystems Foundation Inc</li></ul>
>>> print c.post('/ajax/companies/', {'search': 'adfadfadf'}).content
<ul></ul>

# Get the captcha
>>> _ = c.get(CAPTCHA_URL)
>>> session = c.session._session
>>> captcha = session['vibha.utils.captcha.captcha_solutions'][0]

# Fill the donation form
# We are not yet checking that the form is shown correctly.
>>> _ = c.get(DONATE_URL)
>>> post_dict = {
...  'form_step':        'confirm_details',
...  'email':            'suriya@vibha.org',
...  'first_name':       'Suriya',
...  'last_name':        'Subramanian',
...  'address_1':        '3543 Greystone Dr #1054',
...  'city':             'Austin',
...  'zipcode':          '78731',
...  'state':            unicode(texas.id),
...  'country':          'United States',
...  'phone':            '512-342-9622',
...  'cc_name':           'Suriya N Subramanian',
...  'credit_card':      '4005550000000019',
...  'expr_date_0':      '3',
...  'expr_date_1':      '2008',
...  'cvv':              '3333',
...  'company_name':     microsoft.name,
...  'company_id':      unicode(microsoft.id),
...  'captcha':         captcha,
...  'amount_choice':   '0',
...  'amount':          '223.32',
... }
>>> response = c.post(DONATE_URL, post_dict)
>>> soup = BeautifulSoup(response.content)
>>> print soup.find(name='table', attrs={'class': 'wikitable'})
<table style="margin-left: 2em; margin-right: 2em; font-size: 10pt;" class="wikitable">
<tr>
<td>E-mail</td>
<td>suriya@vibha.org</td>
</tr>
<tr>
<td>First name</td>
<td>Suriya</td>
</tr>
<tr>
<td>Last name</td>
<td>Subramanian</td>
</tr>
<tr>
<td>Address </td>
<td>3543 Greystone Dr #1054<br />
<br />
            Austin, Texas - 78731<br />
            United States</td>
</tr>
<tr>
<td>Phone</td>
<td>512-342-9622</td>
</tr>
<tr>
<td>Credit card</td>
<td>************0019<br />
        Expires: 3/2008</td>
</tr>
<tr>
<td>Donation</td>
<td>$ 223.32</td>
</tr>
<tr>
<td>Referrer Name</td>
<td></td>
</tr>
<tr>
<td>Company/Organization</td>
<td>Microsoft</td>
</tr>
<tr>
<td>Comments</td>
<td></td>
</tr>
</table>

# Check that the value has been posted correctly
>>> session = c.session._session
>>> donation = session['vibha.donations.views.singledonation.donation']
>>> donation['email'] == post_dict['email']
True
>>> donation['first_name'] == post_dict['first_name']
True
>>> donation['last_name'] == post_dict['last_name']
True
>>> donation['address_1'] == post_dict['address_1']
True
>>> donation['city'] == post_dict['city']
True
>>> donation['zipcode'] == post_dict['zipcode']
True
>>> donation['state'] == post_dict['state']
False
>>> donation['state'] == texas
True
>>> donation['country'] == post_dict['country']
True
>>> donation['phone'] == post_dict['phone']
True
>>> donation['credit_card'] == post_dict['credit_card']
True
>>> donation['expr_date_0'] == post_dict['expr_date_0']
Traceback (most recent call last):
...
KeyError: 'expr_date_0'
>>> donation['expr_date'] == [ post_dict['expr_date_0'], post_dict['expr_date_1'] ]
True
>>> donation['amount'] == post_dict['amount']
False
>>> donation['amount']
Decimal("223.32")
>>> donation['company_name'] == post_dict['company_name']
True
>>> type(donation['company_id'])
<type 'int'>
>>> donation['company_id'] == post_dict['company_id']
False
>>> donation['company_id'] == int(post_dict['company_id'])
True
>>> donation['captcha'] == None
True

>>> sorted(donation.keys())
['action_center', 'address_1', 'address_2', 'amount', 'amount_choice', 'captcha', 'cc_name', 'city', 'comments', 'company_id', 'company_name', 'country', 'credit_card', 'cvv', 'email', 'expr_date', 'first_name', 'ip_address', 'last_name', 'phone', 'referrer', 'state', 'zipcode']

# Now post the confirmation form
>>> print c.post(DONATE_URL, {'form_step': 'do_processing'})
Vary: Cookie
Content-Type: text/html; charset=utf-8
Location: http://testserver/donations/single/thanks/
<BLANKLINE>
<BLANKLINE>

# Check that the donation is now added to the database
>>> d = Donation.objects.all()[0]
>>> d.first_name == post_dict['first_name']
True
>>> d.address_1 == post_dict['address_1']
True
>>> d.company == microsoft
True
>>> d.company_name == post_dict['company_name']
True
>>> print d.company_name
Microsoft

############################################################################
# The following code below tests the HTG signup form.

# Before we start, check that we have no signups yet
>>> from vibha.donations.models import HTGSignup
>>> print HTGSignup.objects.all()
[]

# Get a new client because we want to test afresh.
>>> c = Client()
>>> HTG_SIGNUP_URL = '/donations/htg/new/'

# Get the captcha
>>> _ = c.get(CAPTCHA_URL)
>>> session = c.session._session
>>> captcha = session['vibha.utils.captcha.captcha_solutions'][0]

# First just enter the Captcha value
>>> response = c.get(HTG_SIGNUP_URL)
>>> print 'Word Verification' in response.content
True
>>> post_dict = {
... 'captcha': captcha,
... }
>>> response = c.post(HTG_SIGNUP_URL, post_dict)
>>> print 'Word Verification' in response.content
False

# Fill the HTG signup form
# We are not yet checking that the form is shown correctly.
>>> _ = c.get(HTG_SIGNUP_URL)
>>> post_dict = {
...  'email':         'suriya@vibha.org',
...  'first_name':    'Person using credit card',
...  'last_name':     'Subramanian',
...  'address_1':     '3543 Greystone Dr #1054',
...  'city':          'Austin',
...  'zipcode':       '78731',
...  'state':         unicode(texas.id),
...  'country':       'United States of America',
...  'phone':         '512-342-9622',
...  'use_cc':        'Card',
...  'cc_name':       'Suriya N Subramanian',
...  'credit_card':   '4111111111111111',
...  'expr_date_0':   '3',
...  'expr_date_1':   '2008',
...  'amount_choice': '0',
...  'amount':        '23.32',
... }
>>> response = c.post(HTG_SIGNUP_URL, post_dict)
>>> print response
Vary: Cookie
Content-Type: text/html; charset=utf-8
Location: http://testserver/donations/htg/thanks/
<BLANKLINE>
<BLANKLINE>

# Check that the donation is now added to the database
>>> d = HTGSignup.objects.all()[0]
>>> d.first_name == post_dict['first_name']
True
>>> d.use_check == True
False

# Fill the form using check as payment option
>>> _ = c.get(HTG_SIGNUP_URL)
>>> post_dict = {
...  'email':          'suriya@vibha.org',
...  'first_name':     'Person using Check',
...  'last_name':      'Subramanian',
...  'address_1':      '3543 Greystone Dr #1054',
...  'city':           'Austin',
...  'zipcode':        '78731',
...  'state':          unicode(texas.id),
...  'country':        'United States of America',
...  'phone':          '512-342-9622',
...  'use_cc':         'Check',
...  'bank_name':      'University Federal Credit Union',
...  'aba_number':     '123456789',
...  'account_number': '123456789',
...  'amount_choice':  '30.00',
...  'amount':         '23.32',
... }
>>> response = c.post(HTG_SIGNUP_URL, post_dict)
>>> print response
Vary: Cookie
Content-Type: text/html; charset=utf-8
Location: http://testserver/donations/htg/thanks/
<BLANKLINE>
<BLANKLINE>

# Check that the donation is now added to the database
>>> d = HTGSignup.objects.all()[1]
>>> d.first_name == post_dict['first_name']
True
>>> d.use_check == True
True
>>> print d.amount
30.00

# Fill the form using check as payment option, put have some incorrect CC
# fields
>>> _ = c.get(HTG_SIGNUP_URL)
>>> post_dict = {
...  'email':          'suriya@vibha.org',
...  'first_name':     'Person using Check',
...  'last_name':      'Subramanian',
...  'address_1':      '3543 Greystone Dr #1054',
...  'city':           'Austin',
...  'zipcode':        '78731',
...  'state':          unicode(texas.id),
...  'country':        'United States of America',
...  'phone':          '512-342-9622',
...  'use_cc':         'Check',
...  'bank_name':      'University Federal Credit Union',
...  'aba_number':     '123456789',
...  'account_number': '123456789',
...  'cc_name':        'Suriya N Subramanian',
...  'expr_date_0':    '1',
...  'expr_date_1':    '2007',
...  'amount_choice':  '30.00',
...  'amount':         '23.32',
... }
>>> response = c.post(HTG_SIGNUP_URL, post_dict)
>>> print response
Vary: Cookie
Content-Type: text/html; charset=utf-8
Location: http://testserver/donations/htg/thanks/
<BLANKLINE>
<BLANKLINE>
"""
