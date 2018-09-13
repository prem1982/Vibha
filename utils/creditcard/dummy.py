
# $Id: dummy.py 387 2007-08-11 17:18:12Z suriya $

def transact(ccnum, exprdate, amount):
    """
    ccnum: str
    exprdate: str
    amount: Decimal
    """
    status = True
    transid = 0
    transdata = ''
    message = 'Dummy transaction: Nothing happened'
    return status, transid, transdata, message
