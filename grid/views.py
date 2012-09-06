from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.template.loader import get_template

import json

from models import Game, Week

def index(request):
    ben_teams = []
    brian_teams = []

    wk = Week.objects.all()[0];
    for game in wk.games_set():
        if game.picker == "BEN":
            ben_teams.append(game.picked_team)
        else:
            brian_teams.append(game.picked_team)
    interval = 1 * 60 * 1000
    return render_to_response('grid/index.html',
                              {'ben_teams': json.dumps(ben_teams),
                               'brian_teams': json.dumps(brian_teams),
                               'interval': interval
                               },
                              context_instance=RequestContext(request))

def scores(request):
    ret = []
    return HttpResponse(json.dumps(ret), "application/javascript")
