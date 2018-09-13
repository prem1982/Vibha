
from vibha.austinchampion.models import Champion

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

def table_and_chart(total, raised):
    raised_percentage = int(min(100, raised*100/total))
    remaining_percentage = (100 - raised_percentage)
    url = 'http://chart.apis.google.com/chart?cht=p3&chd=t:%d,%d&chs=350x100&chl=Amount%%20Raised|Remaining' % (raised_percentage, remaining_percentage)
    table = """
    <table class="wikitable">
        <tr> <td> Amount Raised </td> <td> $ %s </td> </tr>
        <tr> <td> Goal          </td> <td> $ %s </td> </tr>
    </table>
    """ % (raised, total)
    code = '<center> %s' % table
    if raised_percentage >= 5:
        code += '<img src="%s" />' % url
    code += '</center>'
    return mark_safe(code)

@register.filter
def goal_chart(champion):
    total = champion.goal
    raised = sum(d.amount for d in champion.donation_set.filter(trans_status=True))
    return table_and_chart(total, raised)

@register.filter
def austin_cumulative_goal(unused):
    champions = Champion.objects.all()
    total = sum(c.goal for c in champions)
    raised = sum(sum(d.amount for d in champion.donation_set.filter(trans_status=True)) for champion in champions)
    return table_and_chart(total, raised)
