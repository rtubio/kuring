from django import template

from tasker import models

register = template.Library()


@register.filter(name='status')
def verboseStatus(value):
    for c in models.STATUS_CHOICES:
        if c[0] == value:
            return c[1]
    else:
        return 'N/A'
