from django import template

from tasker.models import Task

register = template.Library()

@register.filter(name='status')
def verboseStatus(value):
    for c in Task.STATUS_CHOICES:
        if c[0] == value:
            return c[1]
    else:
        return 'N/A'
