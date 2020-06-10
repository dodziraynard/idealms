from django.contrib import admin
from .models import TaskHistory, FailedSMS, SentSMS

admin.site.register(TaskHistory)
admin.site.register(FailedSMS)
admin.site.register(SentSMS)
