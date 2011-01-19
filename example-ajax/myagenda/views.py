# Create your views here.
from django.forms.models import modelform_factory
from agenda.models import Recurrence, Event
from django.shortcuts import render_to_response
from django.template.context import RequestContext


def create_event(request):
    event_form = modelform_factory(Event, fields=("begin_date", 
                                                  "start_time", 
                                                  "end_date",
                                                  "end_time",
                                                  "title",
                                                  "description"))()
    recurrence_form = modelform_factory(Recurrence, fields=("frequency", 
                                                            "start_datetime",
                                                            "end_datetime",
                                                            "count",
                                                            "interval"))()
    
    return render_to_response("event_form.html",
                              {'event_form':event_form,
                               'recurrence_form':recurrence_form},
                               context_instance=RequestContext(request))