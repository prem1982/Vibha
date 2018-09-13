
# $Id: spreadsheets.py 419 2007-12-21 04:41:48Z suriya $

# Generate CSV files for models

import csv
from django.utils.encoding import smart_str
from django.db.models.loading import get_model, get_apps, get_models
from django.db.models import BooleanField, FieldDoesNotExist
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template.defaultfilters import yesno, escape

__all__ = ( 'csv_view', 'html_view', )

def _get_field_from_name(model, field_name):
    """Return a field, from the field name of the model."""
    try:
        return model._meta.get_field(field_name)
    except FieldDoesNotExist:
        return getattr(model, field_name)

def _field_extractor_function(field):
    """Return a function that extracts a given field from an instance of a model."""
    if callable(field):
        allow_tags = getattr(field, 'allow_tags', False)
        if allow_tags:
            esc = lambda s: s
        else:
            esc = lambda s: escape(s)
        return (lambda o: esc(smart_str(unicode(field(o)))))
    elif field.choices:
        return (lambda o: getattr(o, 'get_%s_display' % field.name)())
    elif isinstance(field, BooleanField):
        return (lambda o: yesno(getattr(o, field.name), "Yes,No"))
    else:
        return (lambda o: smart_str(unicode(getattr(o, field.name))))

def _header_name(field):
    if callable(field):
        return getattr(field, 'short_description', field.__name__.capitalize())
    else:
        return field.verbose_name

def _get_model_info(app_label, model_name, field_list_var):
    # Get the model
    model = get_model(app_label, model_name)
    if not model:
        raise Http404

    # Ensure that the model has a Spreadsheet class
    try:
        model.Spreadsheet
    except AttributeError:
        class Spreadsheet:
            additional_fields = ()
        model.Spreadsheet = Spreadsheet

    # Fields
    if field_list_var is None:
        fields = model._meta.fields + [ _get_field_from_name(model, field_name) for field_name in model.Spreadsheet.additional_fields ]
    else:
        try:
            fields = [ _get_field_from_name(model, field_name) for field_name in getattr(model.Spreadsheet, field_list_var) ]
        except AttributeError:
            raise Http404

    # Field extractor functions
    field_funcS = [ _field_extractor_function(f) for f in fields ]

    # Field names
    headerS     = [ _header_name(f) for f in fields ]

    return model, headerS, field_funcS

@staff_member_required
def csv_view(request, app_label, model_name, field_list_var=None):
    """Return a CSV file for this table."""

    model, headerS, field_funcS = _get_model_info(app_label, model_name, field_list_var)

    # set the HttpResponse
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s-%s.csv' % (app_label, model_name)
    writer = csv.writer(response, quoting=csv.QUOTE_ALL)

    # Write the header of the CSV file
    writer.writerow(headerS)

    # Write all rows of the CSV file
    for o in model.objects.all().order_by('id'):
        writer.writerow([ func(o) for func in field_funcS ])

    # All done
    return response

@staff_member_required
def html_view(request, app_label, model_name, field_list_var=None):
    """Return a HTML file for this table."""

    model, headerS, field_funcS = _get_model_info(app_label, model_name, field_list_var)

    return render_to_response('utils/html_spreadsheet.html', {
        'objectS': model.objects.all(),
        'headerS': headerS,
        'funcS':   field_funcS, })

# vim:ts=4:sw=4:et:ai:
