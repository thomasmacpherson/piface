from django.shortcuts import render_to_response
from django.http import HttpResponse, QueryDict
from django.template import RequestContext

import piface.pfio as pfio


def index(request):
    pfio.init()
    return render_to_response(
            "httpiface/index.html",
            {'button_range' : range(1, 9)},
            context_instance=RequestContext(request))

def ajax(request):
    data = request.GET.dict()
    returnstr = ""
    if 'write_output' in data:
        output_bitp = int(data['write_output'])
        __write_output(output_bitp)
    
    if 'read_input' in data:
        returnstr += "input_bitp=%d" %__read_input()

    return HttpResponse(returnstr)

def __write_output(output_bitp):
    pfio.write_output(output_bitp)

def __read_input():
    return pfio.read_input()
