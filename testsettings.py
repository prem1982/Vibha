# Django settings for vibha project.

#
# $Id: testsettings.py 426 2008-01-12 01:44:14Z suriya $
#

# Database settings
DATABASE_ENGINE = 'mysql'    # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME =   'suriya_django'
                               # Or path to database file if using sqlite3.
DATABASE_USER = 'suriya_django' # Not used with sqlite3.
DATABASE_PASSWORD = 'e27aea28'   # Not used with sqlite3.
#DATABASE_NAME =   'suriya_donorchoo'
                               # Or path to database file if using sqlite3.
#DATABASE_USER = 'suriya_donorchoo' # Not used with sqlite3.
#DATABASE_PASSWORD = '965c989d'   # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Email
EMAIL_HOST = 'localhost'
EMAIL_PORT = 8025

# Set debugging
TEMPLATE_DEBUG = DEBUG = True
from commonsettings import *

# Set up the logger
import logging
logging.getLogger('').setLevel(logging.DEBUG)

# Set default URLS
LOGIN_REDIRECT_URL = '/portal/projects/'
