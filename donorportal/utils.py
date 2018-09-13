def clean_currency(num):
    try:
        return  long(num.replace('$','').strip())
    except:
        import decimal
        return decimal.Decimal(num.replace('$','').strip())
