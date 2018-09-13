
from django.views.defaults import page_not_found as django_page_not_found
import logging

def page_not_found(request, template_name='404.html'):
    logging.info('Django 404 error: %s', request.path)
    return django_page_not_found(request, template_name)
