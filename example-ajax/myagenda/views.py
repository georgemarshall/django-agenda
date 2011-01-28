# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from .forms import EventForm, RecurrenceForm
from agenda.models import Recurrence, Event
from datetime import date
from agenda.views.date_based import archive, object_detail


def current_month_view(request):
    today = date.today()
    return archive(request, 
                   Event.objects.all(),
                   'begin_date',
                   today.year, 
                   month=today.month, 
                   template_name='current_month_view.html', 
                   template_object_name='event', 
                   extra_context=None)#TODO: add calendar

def show_event(request,year, month, day, slug):
    queryset = Event.objects.all();
    date_field = 'begin_date'
    return object_detail(request, 
                         queryset, 
                         date_field, 
                         year, 
                         month, 
                         day, 
                         slug, 
                         template_name='current_month_view.html', 
                         template_object_name='current_event',
                         extra_context={'event_list' : queryset})
    
def create_event(request):
    has_recurrence = False
    if request.method == "POST":
        event_form = EventForm(request.POST)
        recurrence_form = RecurrenceForm() # in case of event_form is not valid
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
                else :
                    print "RECURRENCE_FORM", recurrence_form.errors
            else:
                event.save()
                return HttpResponse()
        else:
            print "EVENT_FORM", event_form.errors  
    else:
        event_form = EventForm()
        recurrence_form = RecurrenceForm()
        
    return render_to_response("event_form.html",
                              {'event_form':event_form,
                               'recurrence_form':recurrence_form,
                               'has_recurrence' : has_recurrence},
                               context_instance=RequestContext(request))