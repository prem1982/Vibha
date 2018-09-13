
def transact(ccnum, exprdate, amount):
    """
    ccnum: str
    exprdate: str
    amount: Decimal
    """
    amount = str((amount * 100).to_integral())
    import tclink
    params = {
        'custid':    'TestMerchant',
        'password':  'password',
        'action':    'sale',
        'cc':        ccnum,
        'exp':       exprdate,
        'amount':    amount,
        'avs':       'n'
    }
    result = tclink.send(params)
    if result['status'] == 'approved':
        status = True
        message = 'Success'
    else:
        status = False
        message = 'Failure'
    transid = result['transid']
    transdata = str(result)
    return status, transid, transdata, message
