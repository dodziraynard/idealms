from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path('', views.index, name="index"),
    path('welcome', views.welcome, name="welcome"),
    path('staff/', views.staff, name="staff"),
    path('students/', views.students, name="students"),
    path('student_classes/', views.student_classes, name="student_classes"),
    path('student-transcript/', views.transcript, name="transcript"),
    path('subjects/', views.subjects, name="subjects"),
    path('courses/', views.courses, name="courses"),
    path('files/', views.files, name="files"),
    path('records/', views.records, name="records"),
    path('student-report', views.student_reports, name="student_reports"),
    path('map-teacher-to-subject-and-class', views.teacher_subjects, name="teacher_subjects"),
    path('house_masters/', views.house_masters, name="house_masters"),    
    path('grading-system/', views.grading_system, name="grading_system"),    
    path('grading-system/delete/', views.delete_grading_system, name="delete_grading_system"),    
    path('profile', views.profile, name="profile"),    
    path('promotion', views.promotion, name="promotion"),    
    
    path('upload_class_teacher_sheet/', views.upload_class_teacher_sheet, name="upload_class_teacher_sheet"),
    path('upload_house_master_sheet/', views.upload_house_master_sheet, name="upload_house_master_sheet"),
]