from django.shortcuts import render_to_response
from django.template import RequestContext

def timeline(request, model, calendar, past_event_count=None, future_event_count=None, template_name=None, extra_context={}):
    """
    Displays a timeline with past and future events of a given queryset
    """
    past_events = model.objects.past_events().filter(calendars__id=calendar.id)
    if past_event_count:
        past_events = past_events[:past_event_count]

    future_events = model.objects.future_events().filter(calendars__id=calendar.id)
    if future_event_count:
        future_events = future_events[:future_event_count]

    if not template_name:
        template_name = "%s/%s_timeline.html" % (model._meta.app_label, model._meta.object_name.lower())
    
    return render_to_response(template_name=template_name,
                              dictionary={'past_events': past_events,
                                          'future_events': future_events},
                              context_instance=RequestContext(request,
                                                              extra_context),
                              )


