
# $Id: tests.py 411 2007-12-11 03:26:46Z suriya $

"""
>>> from vibha.utils import newforms as vibhaforms
# >>> amount = vibhaforms.FloatField(max_digits=9, required=False, decimal_places=2, help_text='Amount in dollars and cents')
# >>> amount.clean('')
# >>> amount = vibhaforms.FloatField(max_digits=9, decimal_places=2, help_text='Amount in dollars and cents')

>>> amount.clean('')
Traceback (most recent call last):
...
ValidationError: [u'This field is required.']

>>> amount.clean(23.34)
Traceback (most recent call last):
...
ValidationError: [u'Invalid format.']

>>> amount.clean('23.343')
Traceback (most recent call last):
...
ValidationError: [u'Please enter a valid decimal number with at most 2 decimal places.']

>>> amount.clean('233333333333.343')
Traceback (most recent call last):
...
ValidationError: [u'Please enter a valid decimal number with at most 9 total digits.']

>>> amount.clean('12345678.3')
Traceback (most recent call last):
...
ValidationError: [u'Please enter a valid decimal number with a whole part of at most 7 digits.']

>>> amount.clean('hello')
Traceback (most recent call last):
...
ValidationError: [u'Please enter a valid decimal number.']

>>> amount.clean('.34')
Decimal("0.34")

>>> amount.clean('-23.34')
Decimal("-23.34")

>>> amount.clean('23.34')
Decimal("23.34")



>>> from vibha.utils import creditcard
>>> creditcard._verifyMod10('4111111111111111')
True
>>> creditcard._verifyMod10('4111118111111111')
False
>>> creditcard._verifyMod10('')
True

>>> creditcard.isValidCard('4111111111111111')
True
>>> creditcard.isValidCard('4111118111111111')
False
>>> creditcard.isValidCard('')
False

>>> cc = vibhaforms.CreditCardField(required=False)
>>> cc.clean('')

>>> cc = vibhaforms.CreditCardField()
>>> cc.clean('')
Traceback (most recent call last):
...
ValidationError: [u'This field is required.']

>>> cc.clean('hello')
Traceback (most recent call last):
...
ValidationError: [u'Please enter a valid credit card number.']

>>> cc.clean('4111111111111111')
u'4111111111111111'

"""
