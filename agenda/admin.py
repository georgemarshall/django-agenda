from django.contrib import admin
from django.contrib.sites.models import Site

from django.utils.translation import ugettext as _

from .models import Event, Calendar

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'begin_date', 'start_time', 'publish')
    list_display_links = ('title', )
    list_filter = ('begin_date', 'publish', 'author')

    date_hierarchy = 'begin_date'
    
    prepopulated_fields = {"slug": ("title",)}
    
    search_fields = ('title', 'author__username', 'author__first_name', 'author__last_name', 'calendars')

    fieldsets =  ((None, {'fields': ['title', 'slug', 'begin_date', 'start_time', 'end_time', 'description']}),
                  (_('Advanced options'), {'classes' : ('collapse',),
                                           'fields'  : ('publish_date', 'publish', 'sites', 'author', 'allow_comments')}))
    
    # This is a dirty hack, this belongs inside of the model but defaults don't work on M2M
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Makes sure that by default all sites are selected. """
        if db_field.name == 'sites': # Check if it's the one you want
            kwargs.update({'initial': Site.objects.all()})
         
        return super(EventAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
admin.site.register(Event, EventAdmin)

admin.site.register(Calendar)
