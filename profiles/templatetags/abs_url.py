from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def abs_url(context, view_name, *args, **kwargs):
    reversed = reverse(view_name, args=args, kwargs=kwargs)
    if 'request' not in context:
        return reversed
    return context['request'].build_absolute_uri(reversed)

@register.filter
def as_abs_url(path, request):
    return request.build_absolute_uri(path)