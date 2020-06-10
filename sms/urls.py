from django.urls import path
from . import views

app_name = "sms"

urlpatterns = [
    path('', views.index, name="index"),
    path('preview-report', views.preview_report, name="preview_report"),
    path('check-balance', views.check_balance, name="check_balance"),
    path('resend-sms', views.resend_sms, name="resend_sms"),
    path('delete-sms', views.delete_sms, name="delete_sms"),
    path('actions', views.actions, name="actions"),
    path('general', views.general, name="general"),
]
