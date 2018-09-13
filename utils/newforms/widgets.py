
# $Id: widgets.py 407 2007-12-03 05:20:21Z suriya $

from django.forms import widgets as djangowidgets
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django.utils.encoding import smart_unicode, force_unicode
from itertools import chain

__all__ = ('MultiWidget', 'RadioSelect')

class MultiWidget(djangowidgets.MultiWidget):
    def __init__(self, *args, **kwargs):
        super(MultiWidget, self).__init__(*args, **kwargs)

    def decompress(self, value):
        if value is None:
            return [ None for i in self.widgets ]
        super(MultiWidget, self).decompress(value)

# Our own radio box code
# The only difference is, we do not use <ul> like Django does.
class RadioInput(djangowidgets.RadioInput):
    "An object used by RadioFieldRenderer that represents a single <input type='radio'>."

    def __init__(self, name, value, attrs, choice, index, show_br):
	self.show_br = show_br
	super(RadioInput, self).__init__(name, value, attrs, choice, index)

    def __unicode__(self):
        return u'%s %s' % (self.tag(),
                conditional_escape(force_unicode(self.choice_label)))

    def tag(self):
        if 'id' in self.attrs:
            self.attrs['id'] = '%s_%s' % (self.attrs['id'], self.index)
        final_attrs = dict(self.attrs, type='radio', name=self.name, value=self.choice_value)
        if self.is_checked():
            final_attrs['checked'] = 'checked'
        final_attrs['class'] = 'radiofield'
        return mark_safe(u'<input%s />' % flatatt(final_attrs))

class RadioFieldRenderer(djangowidgets.RadioFieldRenderer):

    def __init__(self, name, value, attrs, choices, show_br):
	self.show_br = show_br
	super(RadioFieldRenderer, self).__init__(name, value, attrs, choices)

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield RadioInput(self.name, self.value, self.attrs.copy(), choice, i, self.show_br)

    def __getitem__(self, idx):
        choice = self.choices[idx] # Let the IndexError propogate
        return RadioInput(self.name, self.value, self.attrs.copy(), choice, idx, self.show_br)

    def render(self):
        "Outputs a <ul> for this set of radio fields."
        if self.show_br:
            separator = u'<br />\n'
        else:
            separator = u'\n'
        return mark_safe(u'\n%s\n' % separator.join([u'%s' % force_unicode(w) for w in self]))

class RadioSelect(djangowidgets.RadioSelect):

    def __init__(self, show_br=True, attrs=None, choices=()):
	self.show_br = show_br
	super(RadioSelect, self).__init__(attrs, choices)

    def get_renderer(self, name, value, attrs=None, choices=()):
        "Returns a RadioFieldRenderer instance rather than a Unicode string."
        if value is None: value = ''
        str_value = force_unicode(value) # Normalize to string.
        attrs = attrs or {}
        return RadioFieldRenderer(name, str_value, attrs, list(chain(self.choices, choices)), self.show_br)

