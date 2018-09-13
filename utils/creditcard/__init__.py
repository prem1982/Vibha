
# $Id: __init__.py 401 2007-12-02 01:06:31Z suriya $

import re

from openecho import transact

__all__ = ('transact', 'isValidCard', )

CREDIT_CARD_TYPES = [
	# type,                        prefix, length
	( "Visa",                      "4",    16),
	( "Visa",                      "4",    13),
	( "Mastercard",                "51",   16),
	( "Mastercard",                "52",   16),
	( "Mastercard",                "53",   16),
	( "Mastercard",                "54",   16),
	( "Mastercard",                "55",   16),
	( "Discover",                  "6011", 16),
	( "American Express",          "34",   15),
	( "American Express",          "37",   15),
	( "Diners Club/Carte Blanche", "300",  14),
	( "Diners Club/Carte Blanche", "301",  14),
	( "Diners Club/Carte Blanche", "302",  14),
	( "Diners Club/Carte Blanche", "303",  14),
	( "Diners Club/Carte Blanche", "304",  14),
	( "Diners Club/Carte Blanche", "305",  14),
	( "Diners Club/Carte Blanche", "36",   14),
	( "Diners Club/Carte Blanche", "38",   14),
	( "JCB",                       "3",    16),
	( "JCB",                       "2131", 15),
	( "JCB",                       "1800", 15),
]

def _stripCardNum(number):
    '''Return card number with all non-digits stripped.  '''
    return re.sub(r'[^0-9]', '', number)

def _verifyMod10(number):
    d = 0
    s = 0
    for i in reversed(number):
        for c in str((d + 1) * int(i)): s = s + int(c)
        d = (d + 1) % 2
    return ((s % 10) == 0)

def isValidCard(number):
    number = _stripCardNum(number)
    if not _verifyMod10(number):
        return False
    for name, prefix, length in CREDIT_CARD_TYPES:
        if (len(number) == length) and (number[:len(prefix)] == prefix):
            return True
    return False
