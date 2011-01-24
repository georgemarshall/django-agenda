# Create your views here.
from django.forms.models import modelform_factory
from agenda.models import Recurrence, Event
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from .forms import EventForm, RecurrenceForm
from django.http import HttpResponse


def create_event(request):
    if request.method == "POST":
        event_form = EventForm(request.POST)
        recurrence_form = RecurrenceForm(request.POST)
        if event_form.is_valid():
            event_form.save()
            #TODO: replace HttpResponse by a good HttpResponseRedirect
            return HttpResponse()
        else:
            print event_form.errors
    else:
        event_form = EventForm()
        recurrence_form = RecurrenceForm()
        
    return render_to_response("event_form.html",
                              {'event_form':event_form,
                               'recurrence_form':recurrence_form},
                               context_instance=RequestContext(request))