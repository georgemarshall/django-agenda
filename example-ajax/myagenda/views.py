# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from .forms import EventForm, RecurrenceForm
from agenda.models import Recurrence, Event, Calendar
from datetime import date
from agenda.views.date_based import archive, object_detail


def current_month_view(request):
    today = date.today()
    calendars = Calendar.objects.all()
    month_events = Event.objects.filter(begin_date__month=today.month).order_by('begin_date')
    return archive(request, 
                   Event.objects.all(),
                   'begin_date',
                   today.year, 
                   month=today.month, 
                   template_name='current_month_view.html', 
                   template_object_name='event', 
                   extra_context={'calendars' : calendars,
                                  'month_events' : month_events})#TODO: add calendar

def show_event(request, slug):
    queryset = Event.objects.all();
    event = queryset.get(slug=slug)
    return object_detail(request, 
                         queryset, 
                         'begin_date', 
                         event.begin_date.year, 
                         event.begin_date.month, 
                         event.begin_date.day, 
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
            event = event_form.save()
            has_recurrence = request.POST.get('recurrence', None) 
            if has_recurrence:
                has_recurrence = True #instead of "on"
                data= request.POST.copy()
                data['base_event'] = event.id
                recurrence_form = RecurrenceForm(data)
                if recurrence_form.is_valid():
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