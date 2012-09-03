from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.template.loader import get_template

import json

def index(request):
    interval = 1 * 60 * 1000
    return render_to_response('grid/index.html',
                              {'interval': interval},
                              context_instance=RequestContext(request))

def scores(request):
    ret = []
    return HttpResponse(json.dumps(ret), "application/javascript")
