from urllib.parse import urlparse

from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def webcal(context):
    request = context['request']

    webcal_base_url = reverse('webcal')
    domain = request.build_absolute_uri(webcal_base_url)

    http_url = urlparse(domain)
    webcal_url = http_url.geturl().replace(http_url.scheme, 'webcal', 1)

    return webcal_url
