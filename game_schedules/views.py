# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader


def home(request):
    template = loader.get_template('home.html')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))
