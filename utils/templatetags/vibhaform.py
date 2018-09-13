
# $Id: vibhaform.py 407 2007-12-03 05:20:21Z suriya $

# Template related stuff to customize forms as expected by vibhaform.css
# code.

from django import template
from django.template.defaultfilters import escape
from django.utils.safestring import mark_safe

register = template.Library()

def fieldinfo(field):
    if field.field.required:
        required_class_attrs = { 'class': 'required' }
    else:
        required_class_attrs = {}
    if field.field.help_text:
        help_text = u'<small>%s</small>' % field.field.help_text
    else:
        help_text = u''
    label_code = field.label_tag(escape(field.label), attrs=required_class_attrs)
    if field.errors:
        class_code = u' class="hasformerrors"'
    else:
        class_code = u' class="hasnoformerror"'
    return required_class_attrs, help_text, label_code, class_code

@register.filter
def formfield(field):
    required_class_attrs, help_text, label_code, class_code = fieldinfo(field)
    return mark_safe(u'<div%s>%s%s<br />%s%s</div>' % (class_code, label_code,
            unicode(field), help_text, field.errors))

@register.filter
def formfield_without_label(field):
    required_class_attrs, help_text, label_code, class_code = fieldinfo(field)
    return mark_safe(u'<div%s>%s<br />%s%s</div>' % (class_code, unicode(field), help_text, field.errors))
