from django.shortcuts import render_to_response
from django.http import HttpResponse, QueryDict
from django.template import RequestContext

import piface.pfio as pfio
pfio.init()


def index(request):
    return render_to_response(
            "httpiface/index.html",
            {'button_range' : range(1, 9)},
            context_instance=RequestContext(request))

def ajax(request):
    data = request.GET.dict()
    if 'write_output' in data:
        pfio.write_output(data['write_output'])
        return HttpResponse("")
