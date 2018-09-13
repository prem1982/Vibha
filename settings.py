# Django settings for vibha project.

#
# $Id: settings.py 425 2008-01-12 01:05:22Z suriya $
#

# Database settings
DATABASE_ENGINE = 'mysql'    # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME =   'suriya_django'
                               # Or path to database file if using sqlite3.
DATABASE_USER = 'suriya_django' # Not used with sqlite3.
DATABASE_PASSWORD = 'e27aea28'   # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

EMAIL_HOST_USER = 'suriya'
EMAIL_HOST_PASSWORD = 'd3614f46'
EMAIL_HOST = 'smtp5.webfaction.com'

# Set debugging
TEMPLATE_DEBUG = DEBUG = False
from commonsettings import *

# Set up the logger
import logging
logging.getLogger('').setLevel(logging.INFO)

# Set default URLS
LOGIN_URL = 'https://secure.vibha.org/accounts/login/'
LOGIN_REDIRECT_URL = 'https://secure.vibha.org/portal/projects/'

