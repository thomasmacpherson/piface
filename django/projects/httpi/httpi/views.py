from django.shortcuts import render_to_response
from django.http import HttpResponse, QueryDict
from django.template import RequestContext


def index(request):
    return render_to_response(
            "httpi/index.html",
            {'test' : 1},
            context_instance=RequestContext(request))
