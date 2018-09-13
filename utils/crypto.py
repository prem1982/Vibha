
# $Id: crypto.py 410 2007-12-08 03:38:34Z suriya $

# Some simple functions that build on top of ezPyCrypto.py

import ezPyCrypto
from django.conf import settings
from django.utils.encoding import smart_unicode

public_key = ezPyCrypto.key()
public_key.importKey(settings.PUBLIC_KEY)

private_key = None

def importPrivateKey(passphrase):
    global private_key
    if private_key is None:
        private_key = ezPyCrypto.key()
        private_key.importKey(settings.PUBLIC_AND_PRIVATE_KEY, passphrase=passphrase)

def encrypt(u):
    global public_key
    if not isinstance(u, unicode):
        raise TypeError('encrypt(u): u should be of type unicode')
    s = u.encode(settings.DEFAULT_CHARSET)
    assert isinstance(s, str)
    encrypted = public_key.encStringToAscii(s)
    assert isinstance(encrypted, str)
    return encrypted

def decrypt(s, passphrase=None):
    """
    if passphrase is None, then the key should have already been imported.
    """
#     if not isinstance(s, str):
#         raise TypeError('decrypt(s): s should be of type unicode')
    if not s: return s
    global private_key
    try:
        importPrivateKey(passphrase)
        return smart_unicode(private_key.decStringFromAscii(s))
    except ezPyCrypto.ezPyCryptoException:
        return 'Decryption Failed'
