
# $Id: openecho.py 412 2007-12-11 06:34:52Z suriya $

from urllib import urlencode
import urllib2
from django.conf import settings
import re
from datetime import datetime
import logging
import decimal

# These regular expressions are got from https://wwws.echo-inc.com/ISPGuide-Response.asp
# When a "EV" type operation succeeds, the response has this format.
ECHOTYPE1_APPROVED_FORMAT = re.compile(
r'<!--.<ECHOTYPE1>(?P<approved_response>APPROVED.(?P<cctype>EDS|AMX|DSC).DEPOSITAUTH..NO......(?P<auth_no>[\s\w]{6})AMT.........(?P<amount>[\s\d]{0,5}.\d\d)REFERENCE\#..(?P<ref>\d{8}).V(?P<avs>[XYDMABPWZCGIRSUEN]).*)</ECHOTYPE1>.-->')
ECHOTYPE1_ERROR_FORMAT = re.compile('<!--.<ECHOTYPE1>(?P<error_response>(?P<desc>.{20})(?P<error_code>\d{4}))</ECHOTYPE1>.-->')
ECHOTYPE1_DECLINED_FORMAT = re.compile('<!--.<ECHOTYPE1>(?P<declined_response>DECLINED.(?P<decline_code>\d\d)\s.*)</ECHOTYPE1>.-->')

# Number of times to try the transaction if there is some URLError
NUMTRIES = 2

class EchoPaymentProcessor(object):
    url = settings.ECHO_URL
    configuration = {
        'transaction_type'   : 'EV',
        'order_type'         : 'S',
        'merchant_echo_id'   : settings.ECHO_ID,
        'merchant_pin'       : settings.ECHO_PIN,
        'merchant_email'     : settings.ECHO_MERCHANT_EMAIL,
        'debug'              : settings.ECHO_DEBUG,
    }

    def __init__(self):
        pass

    def prepareData(self, cc_number, ccexp_month, ccexp_year, cnp_security, amount, address_1, zipcode, ip_address):
        now = datetime.now()
        counter = (now.hour * 3600) + (now.minute * 60) + now.second
        assert isinstance(amount, decimal.Decimal)
        cents_amount = (amount * 100).to_integral()
        self.transaction_details = {
            'cc_number'          : cc_number,
            'ccexp_month'        : ccexp_month,
            'ccexp_year'         : ccexp_year,
            'cnp_security'       : cnp_security,
            'grand_total'        : cents_amount,
            'billing_address1'   : address_1,
            'billing_zip'        : zipcode,
            'billing_ip_address' : ip_address,
            'counter'            : counter,
        }

    def parseResults(self, s):
        """
        Parse the response (a list of strings) from the openecho server.

        Returns a 2-tuple, (bool, str) where the bool is success or failure
        of the transaction, the str is a one-line representation of the
        status.
        """
        for line in s:
            if 'ECHOTYPE1' in line:
                match = ECHOTYPE1_APPROVED_FORMAT.match(line)
                if match:
                    return True, match.group('approved_response')
                match = ECHOTYPE1_ERROR_FORMAT.match(line)
                if match:
                    return False, match.group('error_response')
                match = ECHOTYPE1_DECLINED_FORMAT.match(line)
                if match:
                    return False, match.group('declined_response')
                break
        return False, 'Could not parse response from Echo'

    def process(self):
        # Execute the post to openecho.
        query = '%s&%s' % (urlencode(self.configuration), urlencode(self.transaction_details))
        conn = urllib2.Request(url=self.url, data=query)
        numtries = 0
        while True:
            try:
                f = urllib2.urlopen(conn)
                break
            except urllib2.URLError, e:
                logging.exception('EchoPaymentProcessor.process: URLError occured')
                numtries += 1
                if (numtries >= NUMTRIES):
                    logging.error('EchoPaymentProcessor.process: Could not process creditcard transaction. Find out what is wrong')
                    return (False, 'Please try again later', '')
        response = f.readlines()
        f.close()
        status, one_line = self.parseResults(response)
        logging.info('EchoPaymentProcessor.process')
        logging.info('Status: %s', status)
        logging.info('One line response: %s', one_line)
        return (status, one_line, ''.join(response))

def transact(cc_number, ccexp_month, ccexp_year, cnp_security, amount, address_1, zipcode, ip_address):
    logging.info('')
    logging.info('utils.creditcard.openecho.transact')
    logging.info('Expr date: %s/%s', ccexp_month, ccexp_year)
    logging.info('Address: %s, Zip %s', address_1, zipcode)
    logging.info('IP address: %s', ip_address)
    logging.info('Amount: %s', amount)
    p = EchoPaymentProcessor()
    p.prepareData(cc_number, ccexp_month, ccexp_year, cnp_security, amount, address_1, zipcode, ip_address)
    return p.process()
