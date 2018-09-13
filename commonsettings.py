# Django settings for vibha project.

#
# $Id: commonsettings.py 445 2008-03-06 22:26:54Z suriya $
#

import os

VIBHA_DJANGO_ROOT = os.path.abspath(os.path.dirname(__file__))

WHOOSH_INDEX = VIBHA_DJANGO_ROOT

SERVER_EMAIL = DEFAULT_FROM_EMAIL = 'info@vibha.org'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
    #('Suriya Subramanian', 'suriya@vibha.org'),
    #('Raja Gobi',          'crowe_martin@yahoo.com'),
    ('Ramadass Nagarajan', 'ramdas@gmail.com'),
    ('Arvind', 'amenon81+vibha@gmail.com'),    
)

MANAGERS = ADMINS


#########################################################################
# Echo-inc settings for processing credit card transactions
ECHO_URL = 'https://wwws.echo-inc.com/scripts/INR200.EXE'
# This is the correct ID.
ECHO_ID  = '623>9100194'
ECHO_PIN = '93053826'
# The below is the test ID
# ECHO_ID  = '123>4686256'
# ECHO_PIN = '63679135'
ECHO_MERCHANT_EMAIL = 'suriya@vibha.org'
ECHO_DEBUG = 'F'
# You can look at all transactions online. They are available at
# https://wwws.echo-inc.com/Review
# This is only for the test pin.
# The username is suriya
# The password is sachin123
#########################################################################

#########################################################################
# Python logging
import logging
logging.basicConfig(
    level=logging.NOTSET,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %Z',
    filename='/home/suriya/django.log',
    filemode='a',
)
#########################################################################

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 2

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
# This directory is on the host resin.csoft.net
MEDIA_ROOT = '/home/suriya/project-uploads/'

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
# On resin.csoft.net, ~/www/db.vibha.org/project-uploads -> ~/project-uploads
MEDIA_URL = '/project-uploads/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'qdp57jwiyqw*^7ieh$8jaz67%@f5fuwhhu=-irqu=#2jbajg9%'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.http.SetRemoteAddrFromForwardedFor',
    #'vibha.utils.ssl.SSLRedirect',
)


APPEND_SLASH = False

ROOT_URLCONF = 'vibha.urls'

TEMPLATE_DIRS = (
    os.path.join(VIBHA_DJANGO_ROOT, "templates"),
    os.path.join(VIBHA_DJANGO_ROOT, "donor-choose-templates"),
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'vibha.projects',
    'vibha.signups',
    'vibha.dream',
    'vibha.conf07',
    'vibha.donations',
    'vibha.utils',
    'vibha.cfc',
    'vibha.austinchampion',
    'vibha.austincricket08',
    'vibha.triviaguru',
    'django.contrib.admin',
    'django.contrib.sitemaps',
    'vibha.donorportal',
    'vibha.projectfilter',
    'vibha.registration',
    'vibha.pagination',
    'vibha.contact_form',
    'vibha.profiles',
    'vibha.search',

)

#########################################################################
# Our cryptographic keys used for encryption
# see the file vibha/utils/crypto.py
#
# Why/How do we have the private key here?
# The private key is password protected.
#
# The keys below were generated using the following code
# k = ezPyCrypto.key(2048, algoPub=ALGO_PUB, algoSess=ALGO_SESS, # passphrase=something)
# publicKey = k.exportKey()
# publicAndPrivateKey = k.exportKeyPrivate()
# print publicKey, publicAndPrivateKey

KEY_SIZE = 2048
ALGO_PUB = 'RSA'
ALGO_SESS = 'Blowfish'
PUBLIC_KEY = """
<StartPycryptoKey>
KEkwMApOVLUCAAAoVQNSU0FxAChjQ3J5cHRvLlB1YmxpY0tleS5SU0EKUlNBb2JqX2MKcQFvcQJ9
cQQoVQFlcQVMNjU1MzdMClUBbnEGTDIxNzc1OTQ4MDUwOTU2NTYzOTYwMDYyNjIyNzc0OTk5MDY3
NjM2MTg3MTQ5MDg1MjQ2NDExODY0MTkzMzE3Nzk0NzU3MDQzNzM2MzkxMDE0MTU5MzE3OTkwNTUw
NTA4MjQ4MjAwNTk0MDM1Mzk2NDE1Mzg3MzAyMjg3NDQ3NzI0MTkyOTQ1NzI1MjIyNTA4NTE3ODMz
MDQ5Njc1MDU1NDc0MDMzODU4ODE3MzI3MDUxMzE2NjY4MjMzMjMzODE4MDk0Mzg4MDY2NTkzNjA4
MjE3MDM1Njg0OTIxMzY5MzMwMzk0ODA5NTQ3MDMxNjkwNzQ1MTE5NzYzNzQ1MjAxNTMxNjU0NDg1
MDEyODU3NjIxOTM3NzgxOTIwOTAwMTI2Nzk4OTc3NjE4ODAyNzg1MDI5MjUwOTc2MjIyMzkwNzQy
MDA0MzY2OTM2Njk5OTk3MDYzMjYzMzA5MDQ5MDQwNjYyOTk5ODA3ODk5MzM0MzAyMTUxMjU2MTAw
OTM1NTAwMDUxNjEzNTg0OTM2NTY3MTI5OTE3Njk0OTUzNDM1OTAxMjQyNDQ5ODQwMjI4MzMyNjg1
ODY5OTEzNjc4OTY0MjM0MzQzMjU5NzY0Mzc4NDMyNjI5NTk4ODE3NTc1MzcwOTUwNjQ2OTQ4MDY1
NTYzMjU0NzAxMzExNTIwNjE2MzYxODM1NjY5Nzg4MjI4NTA2NDU2Nzg2MTM3NjM2NjkwMDQ0MjA3
OTgzNzgzODEyNzkzMjc4MDUyODkyNjQzNzE2NjAyNTY4OTQzMjA2OTA3MDg4MDYxNzkyOTA5MjM3
NjQ3NDcxMTAyNDUxTAp1YnRxBy5xAHRxAS4=
<EndPycryptoKey>
"""
PUBLIC_AND_PRIVATE_KEY = """
<StartPycryptoKey>
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
n6sOSN1xAHRxAS4=
<EndPycryptoKey>
"""
#########################################################################

# Authentication
AUTH_PROFILE_MODULE = 'registration.UserProfile'
AUTHENTICATION_BACKENDS = (
    'vibha.registration.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)


RECAPTCHA_PUBLIC_KEY = '6Le_swgAAAAAAKIKnNcD9lXRDH5d6H40b99PCQby'
RECAPTCHA_PRIVATE_KEY = '6Le_swgAAAAAAFn3JFvoJTMOQHAIDMftXwX_BJfA'



# Set Sesion Handling
SESSION_EXPIRE_AT_BROWSER_CLOSE = True # Clear the session upon browser exit
SESSION_COOKIE_AGE = 3600 # Time(secs) session is valid
SESSION_SAVE_EVERY_REQUEST = True # This ensures that the expiry time is reset with every request

FILE_UPLOAD_MAX_MEMORY_SIZE = 10000000 #setting to ~10MB


