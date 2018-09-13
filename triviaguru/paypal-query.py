import urllib

query = [
    ('cmd', '_xclick'),
    ('business', 'ramdas@vibha.org'),
    ('item_name', 'Vibha Austin Trivia Guru 2009'),
    ('item_number', team_number),
    ('amount', amount),
    ('page_style', 'Vibha'),
    ('no_shipping', '1'),
    ('return', 'http://www.vibha.org'),
    ('cancel_return', 'http://www.vibha.org'),
    ('cn', team_name),
    ('currency_code', 'USD'),
    ('lc', 'US'),
    ('bn', 'PP-BuyNowBF'),
    ('charset', 'UTF-8'),
]

return ('https://www.paypal.com/cgi-bin/webscr?%s' % urllib.urlencode(query))
