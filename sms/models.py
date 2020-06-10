from django.db import models
from django.utils.translation import ugettext_lazy as _
import jsonfield
from django.utils import timezone

# CELERY
class TaskHistory(models.Model):
    # Relations
    # Attributes - mandatory
    name = models.CharField(max_length=100, verbose_name=_("Task name"), help_text=_("Select a task to record"))
    # Attributes - optional
    history = jsonfield.JSONField(default={}, verbose_name=_("history"), help_text=_("JSON containing the tasks history"))
    
    # Meta & unicode
    class Meta:
        verbose_name = _('Task History')
        verbose_name_plural = _('Task Histories')

    def __str__(self):
        return self.name
        
    def __unicode__(self):
        return _("Task History of Task: %s") % self.name

class FailedSMS(models.Model):
    message = models.TextField()
    number  = models.CharField(max_length=1000)
    name    = models.CharField(max_length=100)
    reason  = models.CharField(max_length=500, null=True, blank=True)
    date    = models.DateTimeField(default=timezone.now)
    code    = models.CharField(max_length=10, null=True, blank=True)

    # Meta & unicode
    class Meta:
        verbose_name = "Failed SMS"
        verbose_name_plural = "Failed SMS"

    def __str__(self):
        return f"{self.name}"

class SentSMS(models.Model):
    message = models.TextField()
    number  = models.CharField(max_length=1000)
    name    = models.CharField(max_length=100)
    date    = models.DateTimeField(default=timezone.now)
    code    = models.CharField(max_length=10, null=True, blank=True)

    # Meta & unicode
    class Meta:
        verbose_name = "Sent SMS"
        verbose_name_plural = "Sent SMS"

    def __str__(self):
        return f"{self.name}"