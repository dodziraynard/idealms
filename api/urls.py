from django.urls import path
from . import views


urlpatterns = [
    path("grading-system", views.grading, name="grading"),
]