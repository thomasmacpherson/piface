from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseBadRequest
from django.template import RequestContext
import simplejson

import piface.pfio as pfio

# fake pfio stuff for testing
outpins = 0
inpins = 0
def fakepfioinit():
    pass
def fakepfiowrite(something):
    global outpins
    outpins = something
def fakepfioreadin():
    return 0b10101010
def fakepfioreadout():
    global outpins
    return outpins
pfio.init = fakepfioinit
pfio.write_output = fakepfiowrite
pfio.read_input = fakepfioreadin
pfio.read_output = fakepfioreadout


def index(request):
    piface_detected = True
    piface_error_msg = ""

    try:
        pfio.init()
    except pfio.InitError as error:
        piface_detected = False
        piface_error_msg = error

    return render_to_response("httpiface/index.html",
            {'button_range' : range(1, 9),
                'piface_detected' : piface_detected,
                'piface_error_msg' : piface_error_msg},
            context_instance=RequestContext(request))

def ajax(request):
    data = request.GET.dict()
    return_values = dict()

    if 'write_output' in data:
        try:
            output_bitp = int(data['write_output'])
        except ValueError:
            return HttpResponseBadRequest("write_output needs an integer bit pattern.")

        __write_output(output_bitp)
    
    if 'read_input' in data:
        return_values.update({'input_bitp' : __read_input()})

    if 'read_output' in data:
        return_values.update({'output_bitp' : __read_output()})

    return HttpResponse(simplejson.dumps(return_values))

def __write_output(output_bitp):
    pfio.write_output(output_bitp)

def __read_input():
    return pfio.read_input()

def __read_output():
    return pfio.read_output()
