from django.db import models

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.conf import settings

from django.contrib.auth.models import User

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager

from django.contrib.sitemaps import ping_google
from django.db.models.signals import post_save
from dateutil import rrule
from datetime import datetime, time, timedelta
from django.db.models import signals
from autoslug import AutoSlugField
from dateutil.relativedelta import relativedelta


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
    begin_date = models.DateField(_('begin date'))
    end_date = models.DateField(_('end date'), null=True)

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
        return _("%(title)s from %(start_datetime)s to %(end_datetime)s") % {
            'title': self.title,
            'start_datetime': self.start_datetime,
            'end_datetime': self.end_datetime
        }

    @models.permalink
    def get_absolute_url(self):
        return ('agenda-detail', (), {
            'year': self.begin_date.year,
            'month': self.begin_date.month,
            'day': self.begin_date.day,
            'slug': self.slug
        })

    # Core fields
    state = models.CharField(_('state'), max_length=1, default='V', choices=STATE_CHOICES)
    title = models.CharField(_('title'), max_length=255)
    slug = AutoSlugField(populate_from='title', 
                         unique=True, 
                         #unique_with='begin_date', 
                         db_index=True,
                         editable=True)

    #Relative to begin_date
    start_time = models.TimeField(_('start time'), blank=True, null=True)
    #Relative to end_date
    end_time = models.TimeField(_('end time'), blank=True, null=True)

    description = models.TextField(_('description'), blank=True, null=True)

    # Extra fields
    add_date = models.DateTimeField(_('add date'), auto_now_add=True)
    mod_date = models.DateTimeField(_('modification date'), auto_now=True)

    author = models.ForeignKey(User, verbose_name=_('author'), db_index=True, blank=True, null=True)

    allow_comments = models.BooleanField(_('Allow comments'), default=True)

    @property
    def start_datetime(self):
        return datetime.combine(self.begin_date, self.start_time)

    @property
    def end_datetime(self):
        return datetime.combine(self.end_date, self.end_time)

    @property
    def duration(self):
        return self.end_datetime - self.start_datetime

    @property
    def is_base_event(self):
        if hasattr(self, "recurrence"):
            return self.recurrence.count() > 0
        return False

    @property
    def is_recurrence(self):
        if hasattr(self, "parent_recurrence"):
            return self.parent_recurrence.count() > 0
        return False

# ping_google can be called by a signal
# TODO rewrite ping_google to be callable by a signal (e.g. add kwargs param)
#post_save.connect(Event, ping_google)

class MetaEvent(Event):
    sub_events = models.ManyToManyField(Event, related_name='meta_event', blank=True, null=True)

    class Meta:
        verbose_name = _('meta event')
        verbose_name_plural = _('meta events')

class Calendar(models.Model):
    name = models.CharField(_('name'), max_length=100, blank=True, null=True)
    events = models.ManyToManyField(Event, related_name='calendars', blank=True, null=True)

    def __unicode__(self):
        if self.name:
            return self.name
        return _("Unnamed Calendar")

FREQUENCY_CHOICES = (
    (rrule.DAILY,   _(u'Daily')),
    (rrule.WEEKLY,  _(u'Weekly')),
    (rrule.MONTHLY, _(u'Monthly')),
#    (rrule.YEARLY,  _(u'Year(s)')),
)

class Recurrence(models.Model):
    """
        This model is used when a event is created and that this event is recurrent.
        It wraps the dateutil.rrule params (http://labix.org/python-dateutil)
    """
    base_event = models.ForeignKey(Event, verbose_name=_('base event'), related_name='recurrence')
    recurrent_events = models.ManyToManyField(Event, verbose_name=_('recurrent events'), related_name='parent_recurrence')

    frequency = models.SmallIntegerField(_('frequency'), choices=FREQUENCY_CHOICES)

    # in most cases, should be base_event.start_datetime
    start_datetime = models.DateTimeField(_('recurrence begin date'), blank=True, null=True) #rrule dtstart
    end_datetime = models.DateTimeField(_('end date'), blank=True, null=True) # rrule until

    interval = models.PositiveIntegerField(_('interval'), blank=True, null=True)
    count = models.PositiveIntegerField(_('count'), blank=True, null=True)

    def save(self, **kwargs):
        if not self.start_datetime:
            self.start_datetime = self.base_event.start_datetime

        self.start_datetime = self.start_datetime.replace(minute=self.base_event.start_time.minute, hour=self.base_event.start_time.hour)

        if not self.count and not self.end_datetime:
            self.end_datetime = self.start_datetime + relativedelta(years=+1)

        models.Model.save(self)

def create_recurrence(sender, instance, created, **kwargs):
    if created:
        options = {'dtstart' : instance.start_datetime}
        if instance.end_datetime:
            options['end_datetime'] = instance.end_datetime
        elif instance.count:
            options['count'] = instance.count + 1 #because the base_event date counts for one (the first)
        if instance.interval:
            options['interval'] = instance.interval
        occurs = rrule.rrule(instance.frequency, **options)
        event_class = kwargs.get('event_class', Event)
        for o in occurs:
            if o != instance.start_datetime:
                base_event = instance.base_event
                event = event_class.objects.create(title=base_event.title, begin_date=o, start_time=base_event.start_time, end_date=o + base_event.duration, end_time=base_event.end_time, description=base_event.description)
                instance.recurrent_events.add(event)
    else:
        pass
