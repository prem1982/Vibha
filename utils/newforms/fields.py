
# $Id: fields.py 415 2007-12-12 22:05:58Z suriya $

#from django.core import validators
from django import forms
from django.utils.encoding import smart_unicode
from django.utils.dates import MONTHS
from vibha.utils import creditcard
from vibha.utils.captcha import check_captcha
import decimal
import datetime

__all__ = (
    'CreditCardField',
    'ABANumberField',
    'ForeignKeyChoiceField',
    'AnotherChoiceField',
    'MultiValueField',
    'MonthField',
    'YearField',
    'MonthYearField',
    'CharField',
    'EmailField',
)

EMPTY_VALUES = (None, '')

class CreditCardField(forms.RegexField):
    def __init__(self, *args, **kwargs):
        super(CreditCardField, self).__init__(regex=r'^\d{13,16}$',
                max_length=16, error_message=u'Please enter a valid credit card number.', *args, **kwargs)

    def clean(self, value):
        super(CreditCardField, self).clean(value)
        if value in EMPTY_VALUES:
            return None
        if creditcard.isValidCard(value):
            return smart_unicode(value)
        else:
            raise forms.ValidationError(u'Please enter a valid credit card number.')

class ABANumberField(forms.RegexField):
    def __init__(self, *args, **kwargs):
        super(ABANumberField, self).__init__(regex=r'^\d{9}$',
                max_length=9, error_message=u'Please enter a valid ABA Routing number.', *args, **kwargs)

class ForeignKeyChoiceField(forms.ChoiceField):
    def __init__(self, empty_choice=u'----', *args, **kwargs):
        self.empty_choice = empty_choice
        super(ForeignKeyChoiceField, self).__init__(choices=(), *args, **kwargs)

    def _fill_choices(self, querylist):
        self.querylist = querylist
        self.choices = [(u'', self.empty_choice)] + [(i.id, unicode(i)) for i in querylist]

    def clean(self, value):
        super(ForeignKeyChoiceField, self).clean(value)
        if value in EMPTY_VALUES:
            return None
        try:
            return self.querylist.get(id=int(value))
        except:
            raise forms.ValidationError(u'Please select a proper value')

class AnotherChoiceField(forms.ChoiceField):
    def __init__(self, empty_choice=u'----', *args, **kwargs):
        self.empty_choice = empty_choice
        super(AnotherChoiceField, self).__init__(*args, **kwargs)

    def _fill_choices(self):
        self.choices = [(u'', self.empty_choice)] + self.choices

    def clean(self, value):
        super(AnotherChoiceField, self).clean(value)
        if value in EMPTY_VALUES:
            return None
        return value

class MultiValueField(forms.MultiValueField):
    def __init__(self, fields=(), *args, **kwargs):
        # Relative import 
        from widgets import MultiWidget
        widgets = MultiWidget(widgets = [ f.widget for f in fields ])
        super(MultiValueField, self).__init__(fields=fields, widget=widgets, *args, **kwargs)

    def compress(self, data_list):
        return data_list


class MonthField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        super(MonthField, self).__init__(choices=MONTHS.items(), *args, **kwargs)

CURRENT_YEAR = datetime.date.today().year
YEARS  = range(CURRENT_YEAR, CURRENT_YEAR+10)
class YearField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        super(YearField, self).__init__(choices=[(y,y) for y in YEARS], *args, **kwargs)

class MonthYearField(MultiValueField):
    def __init__(self, *args, **kwargs):
        super(MonthYearField, self).__init__(fields=(MonthField(), YearField()), *args, **kwargs)

DEFAULT_CHARFIELD_SIZE = 35
class CharField(forms.CharField):
    def widget_attrs(self, widget):
        if isinstance(widget, (forms.TextInput, forms.PasswordInput)):
            return {'size': widget.attrs.get('size', DEFAULT_CHARFIELD_SIZE)}

class EmailField(forms.EmailField):
    def widget_attrs(self, widget):
        if isinstance(widget, forms.TextInput):
            return {'size': widget.attrs.get('size', DEFAULT_CHARFIELD_SIZE)}
