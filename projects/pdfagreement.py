
# $Id: pdfagreement.py 297 2007-04-07 00:37:52Z suriya $

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from django.template.loader import render_to_string
from django.http import HttpResponse

# Keep the styles handy
TITLE = getSampleStyleSheet()['Title']
NORMAL = getSampleStyleSheet()['Normal']
BULLET = getSampleStyleSheet()['Bullet']
HEADING1 = getSampleStyleSheet()['Heading1']
HEADING2 = getSampleStyleSheet()['Heading2']
# Our default font
CUSTOM = ParagraphStyle('CustomNormal', NORMAL)
CUSTOM.fontSize = 12
CUSTOM.spaceAfter = 12
CUSTOM.spaceBefore = 12
CUSTOM.leading = 14
# Our bullets font
CUSTOM_BULLETS = ParagraphStyle('CustomBullet', BULLET)
CUSTOM_BULLETS.fontSize = 12
CUSTOM_BULLETS.spaceAfter = 12
CUSTOM_BULLETS.spaceBefore = 12
CUSTOM_BULLETS.bulletFontName = 'Symbol'
CUSTOM_BULLETS.bulletIndent = 18
CUSTOM_BULLETS.leftIndent = 32
CUSTOM.leading = 14


PAGE_WIDTH, PAGE_HEIGHT = letter
theDate = 'hello world'

def myFirstPage(canvas, doc):
    canvas.saveState()
    # Setting PDF file information
    canvas.setAuthor('Help Them Grow Inc.')
    canvas.setTitle('Project partnership agreement')
    canvas.setSubject('')
    # Header
    canvas.setFont( 'Times-Bold', 16 )
    canvas.drawCentredString( PAGE_WIDTH/2.0, PAGE_HEIGHT- (0.25*inch), 'Vibha' )
    canvas.line( 0.5*inch, PAGE_HEIGHT - (0.35*inch), PAGE_WIDTH - (0.5*inch), PAGE_HEIGHT - (0.35*inch) )
    canvas.setFont( 'Times-Bold', 8 )
    canvas.drawCentredString( PAGE_WIDTH/2.0, PAGE_HEIGHT- (0.50*inch), 'Hello Address' )
    # Footer
    canvas.setFont( 'Times-Roman', 9 )
    canvas.drawString( 0.5*inch, 0.75*inch, 'First Page' )
    # Image
    canvas.restoreState()

def myLaterPages(canvas, doc ):
    canvas.saveState()
    # Header
    canvas.setFont( 'Times-Roman', 9 )
    canvas.drawString( 0.5*inch, PAGE_HEIGHT- (0.5*inch), 'Page %d' % doc.page )
    canvas.drawRightString( PAGE_WIDTH - (0.5*inch), PAGE_HEIGHT - (0.5*inch), theDate )
    # Footer.
    canvas.drawString( inch, 0.5*inch, 'Page %d' % doc.page )
    canvas.restoreState()

def makePara(s):
    if s.startswith('#'):
        return Paragraph(s[1:], HEADING2)
    elif s.startswith('$'):
        return Paragraph(s[1:], TITLE)
    elif s.startswith('*'):
        return Paragraph(s[1:], CUSTOM_BULLETS, bulletText='@')
    else:
        return Paragraph(s, CUSTOM)

def createStory(context):
    s = render_to_string('projects/project-agreement.txt', context)
    return [ makePara(i) for i in s.split('\n\n') ]

def pdfagreement(filename, context):
    # Take a look at http://www.djangoproject.com/documentation/outputting_pdf/
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(response, pagesize=letter, leftMargin=0.5*inch, rightMargin=0.5*inch, bottomMargin=1.5*inch)
    doc.build(createStory(context), onFirstPage=myFirstPage, onLaterPages=myLaterPages)

    return response

# vim:ts=4:sw=4:et
