from django.core import serializers
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.template.loader import get_template

import json

from models import Game, Week

def index(request):
    ben_teams = []
    brian_teams = []

    wk = Week.objects.latest()
    for game in wk.game_set.all():
        picked = game.picked_team
        other = game.away_team if game.home_team == picked else game.home_team
        if game.picker == "BEN":
            ben_teams.append(picked)
            brian_teams.append(other)
        else:
            brian_teams.append(picked)
            ben_teams.append(other)
    interval = 1 * 60 * 1000
    return render_to_response('grid/index.html',
                              {'ben_teams': json.dumps(ben_teams),
                               'brian_teams': json.dumps(brian_teams),
                               'interval': interval
                               },
                              context_instance=RequestContext(request))

def scores(request):
    wk = Week.objects.latest()
    games = wk.game_set.all()
    ret = serializers.serialize('json', games)
    return HttpResponse(ret, "application/javascript")
