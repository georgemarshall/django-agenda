from datetime import datetime

from django.db import models

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.conf import settings

from django.contrib.auth.models import User

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager

from django.contrib.sitemaps import ping_google


class PublicationManager(CurrentSiteManager):
    def get_query_set(self):
        return super(CurrentSiteManager, self).get_query_set().filter(publish=True, publish_date__lte=datetime.now())

class EventManager(models.Manager):
    def past_events(self):
        return self.get_query_set().filter(begin_date__lt=datetime.now())

    def future_events(self):
        """
        Returns present and future events
        """
        return self.get_query_set().filter(begin_date__gte=datetime.now()).order_by('begin_date', 'start_time')


class AbstractEvent(models.Model):
    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')

        abstract = True

    # Custom managers
    objects = EventManager()
    on_site = CurrentSiteManager()
    published = PublicationManager()

    # Fields
    begin_date = models.DateField(_('date'))
    end_date = models.DateField(_('date'), null=True)

    publish_date = models.DateTimeField(_('publication date'), default=datetime.now())
    publish = models.BooleanField(_('publish'), default=True)

    sites = models.ManyToManyField(Site)

class Event(AbstractEvent):
    STATE_CHOICES = (
        ('V', _('Valid')),
        ('C', _('Canceled')),
        ('P', _('Postponed')),
        )

    class Meta:
        ordering = ['-begin_date', '-start_time', '-title']
        get_latest_by = 'begin_date'
        permissions = (("change_author", ugettext("Change author")),)
        unique_together = ("begin_date", "slug")

    def __unicode__(self):
        return _("%(title)s on %(begin_date)s") % { 'title'      : self.title,
                                                    'begin_date' : self.begin_date }
    @models.permalink                                               
    def get_absolute_url(self):
        return ('agenda-detail', (), {'year'  : self.begin_date.year, 
                                      'month' : self.begin_date.month, 
                                      'day'   : self.begin_date.day, 
                                      'slug'  : self.slug }
                )
        
    # Core fields
    state = models.CharField(_('state'), max_length=1, default='V', choices=STATE_CHOICES)
    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('slug'), db_index=True)

    #Relative to begin_date
    start_time = models.TimeField(_('start time'), blank=True, null=True)
    #Relative to end_date
    end_time = models.TimeField(_('end time'), blank=True, null=True)
    
    description = models.TextField(_('description'))

    # Extra fields
    add_date = models.DateTimeField(_('add date'), auto_now_add=True)
    mod_date = models.DateTimeField(_('modification date'), auto_now=True)
    
    author = models.ForeignKey(User, verbose_name=_('author'), db_index=True, blank=True, null=True)
    
    allow_comments = models.BooleanField(_('Allow comments'), default=True)

    
    def save(self):
        super(Event, self).save()
        if not settings.DEBUG:
            try:
                ping_google()
            except Exception:
                import logging
                logging.warn('Google ping on save did not work.')

class Calendar(models.Model):
    name = models.CharField(_('name'), max_length=100, blank=True, null=True)

    events = models.ManyToManyField(Event, related_name='calendars', blank=True, null=True)

    def __unicode__(self):
        if self.name:
            return self.name
        return _("Unnamed Calendar")
