from django.urls import path
from . import views

app_name = "student"

urlpatterns = [
    path('one_report_preview', views.one_report_preview, name="one_report_preview"),
    path('', views.student, name="student"),
    path('login', views.student_login, name="login"),
]


