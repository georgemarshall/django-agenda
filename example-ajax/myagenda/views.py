# Create your views here.
from django.forms.models import modelform_factory
from agenda.models import Recurrence, Event
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from .forms import EventForm, RecurrenceForm
from django.http import HttpResponse


def create_event(request):
    has_recurrence = False
    if request.method == "POST":
        event_form = EventForm(request.POST)
        if event_form.is_valid():
            event = event_form.save(commit=False)
            has_recurrence = request.POST.get('recurrence', None) 
            if has_recurrence:
                has_recurrence = True #instead of "on"
                recurrence_form = RecurrenceForm(request.POST, initial={'base_event' : event})
                if recurrence_form.is_valid():
                    event.save()
                    recurrence_form.save()
                    return HttpResponse() 
            #TODO: replace HttpResponse by a good HttpResponseRedirect
            else:
                return HttpResponse()
        else:
            print event_form.errors
    else:
        event_form = EventForm()
        recurrence_form = RecurrenceForm()
        
    return render_to_response("event_form.html",
                              {'event_form':event_form,
                               'recurrence_form':recurrence_form,
                               'has_recurrence' : has_recurrence},
                               context_instance=RequestContext(request))