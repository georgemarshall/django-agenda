from django.conf.urls.defaults import *

# place app url patterns here

from .views import create_event

urlpatterns = patterns('',
    (r'^', include('agenda.urls')),
    url(r'^event/create/', create_event, name="myagenda_create_event"),
)