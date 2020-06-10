from django.conf.urls import include
from django.urls import path
from . import views

app_name = 'pdf'

urlpatterns = [
    path("<str:academic_year>/<str:semester>/<str:student_id>", views.GenerateReportPDF.as_view(), name='render_pdf'),
    path("students/<str:student_class_id>/<str:academic_year>/<str:semester>", views.GenerateReportAllStudents.as_view(), name='students_render_pdf'),
    path("class-transcript/", views.GenerateTranscriptPDF.as_view(), name='class_transcript'),
    path("student-transcript/", views.GenerateStudentTranscriptPDF.as_view(), name='student_transcript'),
]
