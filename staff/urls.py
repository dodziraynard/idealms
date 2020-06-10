from django.urls import path
from . import views, ajax

app_name = "staff"

urlpatterns = [
    path('welcome', views.welcome, name="welcome"),
    path('select_class/<str:subject_id>', views.select_class, name="select_class"),
    path('drop_subjects', views.drop_subjects, name="drop_subjects"),
    path('subject_teacher', views.subject_teacher, name="subject_teacher"),
    path('house-master', views.house_master, name="house_master"),
    path('form-teacher', views.form_teacher, name="form_teacher"),
    path('student-report', views.student_reports, name="student_reports"),
    path('input_form_master_remarks', views.input_form_master_remarks, name="input_form_master_remarks"),
    path('input_subject_records', views.input_subject_records, name="input_subject_records"),
    path('input_house_master_remarks', views.input_house_master_remarks, name="input_house_master_remarks"),
    path('preview_added_records', views.preview_added_records, name="preview_added_records"),


    # AJAX
    path('get_form_teacher_remark_input_template', ajax.get_form_teacher_remark_input_template),
    path('get_previous_remark', ajax.get_previous_remark),
    path('save_form_teacher_remark', ajax.save_form_teacher_remark),
    path('get_academic_record', ajax.get_academic_record),
    path('get_subject_score_input_template', ajax.get_subject_score_input_template),
    path('save_subject_record', ajax.save_subject_record),
    path('house_master_remark_template', ajax.get_house_master_input_template),
    path('save_house_master_remark', ajax.save_house_master_remark),
    path('get_previous_house_master_remark', ajax.get_previous_house_master_remark),
    path('generate_record_sheet', ajax.generate_record_sheet, name="generate_record_sheet"),
    path('generate_house_master_remark_sheet', ajax.generate_house_master_remark_sheet, name="generate_house_master_remark_sheet"),
    path('generate_form_master_remark_sheet', ajax.generate_form_master_remark_sheet, name="generate_form_master_remark_sheet"),


    # Uploads
    path('records/upload', views.upload_record, name="upload_record"),
    path('remarks/form-teacher/upload', views.upload_form_teacher_remarks, name="upload_form_teacher_remarks"),
    path('remarks/house-master/upload', views.upload_house_master_remarks, name="upload_house_master_remarks"),
]