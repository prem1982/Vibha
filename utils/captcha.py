
# $Id: captcha.py 370 2007-06-19 16:59:35Z suriya $

# Generate a Captcha

from Captcha.Visual.Tests import PseudoGimpy
from django.http import HttpResponse
from django.contrib.formtools.preview import FormPreview

PREFIX = 'vibha.utils.captcha'
CAPTCHA_SOLUTIONS = PREFIX + '.captcha_solutions'
HUMAN_FLAG = PREFIX + '.human_flag'

def captcha_image(request):
    # set the HttpResponse
    response = HttpResponse(mimetype='image/png')
    g = PseudoGimpy()
    i = g.render()
    i.save(response, 'png')
    solutions = g.solutions
    request.session[CAPTCHA_SOLUTIONS] = solutions
    return response

def check_captcha(request, value):
    if request is not None:
        solutions = request.session.get(CAPTCHA_SOLUTIONS, None)
        human_flag = (solutions is not None) and (value in solutions)
        request.session[HUMAN_FLAG] = human_flag
        return human_flag
    else:
        return False

def is_human(request):
    return (request is not None) and request.session.get(HUMAN_FLAG, False)

# vim:ts=4:sw=4:et:ai:
