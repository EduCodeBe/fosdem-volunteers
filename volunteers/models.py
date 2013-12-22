from django.db import models
from django.contrib.auth.models import User
from userena.models import UserenaLanguageBaseProfile
from django.utils.translation import ugettext_lazy as _
import datetime

# Create your models here.

class Edition(models.Model):
    class Meta:
        verbose_name = _('Edition')
        verbose_name_plural = _('Editions')

    def __unicode__(self):
        return unicode(self.year)

    year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()


"""
A track is a collection of talks, grouped around one single
concept or subject.
"""
class Track(models.Model):
    class Meta:
        verbose_name = _('Track')
        verbose_name_plural = _('Tracks')

    def __unicode__(self):
        return self.title

    title = models.CharField(max_length=128)
    description = models.TextField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()


class Talk(models.Model):
    class Meta:
        verbose_name = _('Talk')
        verbose_name_plural = _('Talks')

    def __unicode__(self):
        return self.title

    track = models.ForeignKey(Track)
    title = models.CharField(max_length=128)
    speaker = models.CharField(max_length=50)
    description = models.TextField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()


"""
Categories are things like buildup, cleanup, moderation, ...
"""
class TaskCategory(models.Model):
    class Meta:
        verbose_name = _('Task Category')
        verbose_name_plural = _('Task Categories')

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=50)
    description = models.TextField()
    volunteers = models.ManyToManyField('Volunteer', through='VolunteerCategory', blank=True, null=True)

    def assigned_volunteers(self):
        return self.volunteer_set.count()


"""
A task template contains all the data about a task that isn't task specific.
For example, cleanup can happen in multiple locations or at multiple times.
Not sure we need this, but it seemed like a good thing to have when I wrote
down the DB model. ;)
"""
class TaskTemplate(models.Model):
    class Meta:
        verbose_name = _('Task Template')
        verbose_name_plural = _('Task Templates')

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=50)
    description = models.TextField()
    category = models.ForeignKey(TaskCategory)


"""
Contains the specifics of an instance of a task. It's based on a task template
but it can override the name and description, yet not the category.
"""
class Task(models.Model):
    class Meta:
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=50)
    description = models.TextField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    nbr_volunteers = models.IntegerField()
    # Only for moderation, or possible future tasks related
    # to a specific talk.
    talk = models.ForeignKey(Talk, blank=True, null=True)
    template = models.ForeignKey(TaskTemplate)
    volunteers = models.ManyToManyField('Volunteer', through='VolunteerTask', blank=True, null=True)

    def assigned_volunteers(self):
        return self.volunteer_set.count()


"""
The nice guys n' gals who make it all happen.
"""
class Volunteer(UserenaLanguageBaseProfile):
    class Meta:
        verbose_name = _('Volunteer')
        verbose_name_plural = _('Volunteers')

    def __unicode__(self):
        return self.name

    user = models.OneToOneField(User, unique=True, verbose_name=_('user'), related_name='volunteer')
    name = models.CharField(max_length=50)
    email = models.EmailField()
    # Categories in which they're interested to help out.
    categories = models.ManyToManyField(TaskCategory, through='VolunteerCategory', blank=True, null=True)
    # Tasks for which they've signed up.
    tasks = models.ManyToManyField(Task, through='VolunteerTask', blank=True, null=True)
    editions = models.ManyToManyField(Edition, through='VolunteerStatus', blank=True, null=True)
    signed_up = models.DateField(default=datetime.date.today)
    about_me = models.TextField(_('about me'), blank=True)


"""
Many volunteers come back year after year, but sometimes they
take a hiatus of one or multiple years. This is there to capture
their availability on a per-event basis, in order to filter out
inactive volunteers from the selection pool.
"""
class VolunteerStatus(models.Model):
    class Meta:
        verbose_name = _('Volunteer Status')
        verbose_name_plural = _('Volunteer Statuses')

    def __unicode__(self):
        return '%s - %s: %s' % (self.volunteer.name,
            self.edition.year,
            'Yes' if self.active else 'No')

    active = models.BooleanField()
    volunteer = models.ForeignKey(Volunteer)
    edition = models.ForeignKey(Edition)


"""
M2M tables because I want to have the relationship on both model admin pages
"""
class VolunteerTask(models.Model):
    class Meta:
        verbose_name = _('VolunteerTask')
        verbose_name_plural = _('VolunteerTasks')

    def __unicode__(self):
        return self.task

    volunteer = models.ForeignKey(Volunteer)
    task = models.ForeignKey(Task)


class VolunteerCategory(models.Model):
    class Meta:
        verbose_name = _('VolunteerCategory')
        verbose_name_plural = _('VolunteerCategories')

    def __unicode__(self):
        return self.category

    volunteer = models.ForeignKey(Volunteer)
    category = models.ForeignKey(TaskCategory)