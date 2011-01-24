# Create your views here.
from django.forms.models import modelform_factory
from agenda.models import Recurrence, Event
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from .forms import EventForm, RecurrenceForm


def create_event(request):
    event_form = EventForm()
    recurrence_form = RecurrenceForm()
    
    return render_to_response("event_form.html",
                              {'event_form':event_form,
                               'recurrence_form':recurrence_form},
                               context_instance=RequestContext(request))