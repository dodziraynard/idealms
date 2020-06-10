from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from django.views.generic import View
from re import template
from pdfgenerator.utils import render_to_pdf
import datetime
from student.models import Student, StudentClass, HouseMasterRemarks, ClassTeacherRemarks, Record
from school.models import School
from django.contrib.auth.models import User
from helpers.functions import redirect_handler

# Individual students
class GenerateReportPDF(View):
    def get(self, request, academic_year, semester, student_id):
        if not request.user.is_authenticated:
            return redirect_handler(request, "student:login", {"next":request.META.get("PATH_INFO")})   

        academic_year       = "/".join(academic_year.split("-"))
        student_id          = "/".join(student_id.split("-"))
        semester            = " ".join(semester.split("-")).title()
        
        # Authenticating logged in student
        student = Student.objects.filter(student_id=student_id).first()
        if student:
            if request.user_type == "student":
                if not request.user.student.student_id == student_id:
                    return redirect_handler(request, "student:login", {"next":request.META.get("PATH_INFO")})   


            teacher_remarks = ClassTeacherRemarks.objects.filter(student__student_id=student_id, 
                                                    semester=semester, 
                                                    academic_year=academic_year, 
                                                    ).first()

            house_master_remarks = HouseMasterRemarks.objects.filter(student__student_id=student_id, 
                                                    semester=semester, 
                                                    academic_year=academic_year).first()
                                                
            elective_records = Record.objects.filter(semester=semester,
                                                     academic_year = academic_year,
                                                     student__student_id = student_id,
                                                     subject__is_elective = True,
                                                )
            
            core_records = Record.objects.filter(semester=semester,
                                                academic_year = academic_year,
                                                student__student_id=student_id, 
                                                subject__is_elective = False,
                                            )
            
            # Getting class of record
            record = elective_records.first() or core_records.first()
            student_class = record.record_class
            print(student_class)

            context = {
                "academic_year": academic_year,
                "semester": semester,
                "elective_records": elective_records,
                "core_records": core_records,
                "teacher_remarks": teacher_remarks, 
                "house_master_remarks": house_master_remarks,
                "school": School.objects.all().first(),
                "student" : student,
                "student_class" : student_class,
                "current_time":datetime.datetime.now()
            }
        else:
            context = {
                "error_message":f"Student with id '{student_id}' not found",
            }
        pdf = render_to_pdf('pdf/report_pdf.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "%s.pdf" % ("Reports")
            content = "inline; filename='%s'" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")

# Report for all students
class GenerateReportAllStudents(View):
    def get(self, request, student_class_id, academic_year, semester):        
        if request.user.is_authenticated:
            if request.user_type == "student":
                return redirect_handler(request, "accounts:login", {"next":request.META.get("PATH_INFO")})
        else:
            return redirect_handler(request, "accounts:login", {"next":request.META.get("PATH_INFO")})
                
        academic_year       = "/".join(academic_year.split("-"))
        semester            = " ".join(semester.split("-")).title()
        student_class       = get_object_or_404(StudentClass, student_class_id=student_class_id)

        students = Student.objects.filter(student_class=student_class)
        student_teacher_remarks = {}
        student_house_master_remarks = {}
        student_core_records = {}
        student_elective_records= {}

        for student in students:
            teacher_remarks = ClassTeacherRemarks.objects.filter(student = student, 
                                                    semester=semester, 
                                                    academic_year=academic_year, 
                                                    ).first()
            student_teacher_remarks.update({student:teacher_remarks})

            house_master_remarks = HouseMasterRemarks.objects.filter(student = student,
                                                    semester=semester, 
                                                    academic_year=academic_year).first()

            student_house_master_remarks.update({student:house_master_remarks})

            elective_records = Record.objects.filter(semester=semester,
                                                    academic_year = academic_year,
                                                    student = student,
                                                    subject__is_elective = True,
                                                )
            student_elective_records.update({student:elective_records})
            
            core_records = Record.objects.filter(semester=semester,
                                                academic_year = academic_year,
                                                student = student,
                                                subject__is_elective = False,
                                            )
            student_core_records.update({student:core_records})

        context = {
            "students":students,
            "academic_year":academic_year,
            "semester":semester,
            "student_teacher_remarks": student_teacher_remarks,
            "student_house_master_remarks": student_house_master_remarks,
            "student_core_records": student_core_records,
            "student_elective_records": student_elective_records,
            "school": School.objects.all().first(),
            "class":student_class,
            "current_time":datetime.datetime.now()
        }

        pdf = render_to_pdf('pdf/class_report_pdf.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "%s.pdf" % ("Reports")
            content = "inline; filename='%s'" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")

# Transcript for students in a class
class GenerateTranscriptPDF(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect_handler(request, "student:login", {"next":request.META.get("PATH_INFO")})   

        class_id       = request.GET.get("class_id")
        student_class = StudentClass.objects.filter(student_class_id=class_id).first()
        if student_class:
            student_transcript = {}
            student_forms = {}
            student_semesters = {}
            students = Student.objects.filter(student_class=student_class)
            if students:
                for student in students:
                    records = Record.objects.filter(student=student).order_by("-date")
                    semesters   = records.values("semester").order_by("semester").distinct()
                    
                    forms  = []
                    for item in records:
                        if not item.record_class.form in forms:
                            forms.append(item.record_class.form)
                    student_transcript.update({student:records})
                    student_forms.update({student:forms})
                    student_semesters.update({student:semesters})

            context = {
                "student_transcript":student_transcript,
                "student_forms":student_forms,
                "student_semesters":student_semesters,
                "request":request,
            }
        else:
            context = {
                "error_message": f"Class with id '{class_id}' not found",
            }

        pdf = render_to_pdf('pdf/class_transcript.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "%s.pdf" % ("Reports")
            content = "inline; filename='%s'" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")

# Transcript for a student
class GenerateStudentTranscriptPDF(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect_handler(request, "student:login", {"next":request.META.get("PATH_INFO")})   
        
        student_id       = request.GET.get("student_id")
        student          = Student.objects.filter(student_id=student_id).first()
        records          = Record.objects.filter(student=student).order_by("-date")
        semesters        = records.values("semester").order_by("semester").distinct()

        forms  = []
        for item in records:
            if not item.record_class.form in forms:
                forms.append(item.record_class.form)

        if student:
            context = {
                "student":student,
                "forms":forms,
                "semesters":semesters,
                "records":records,
                "request":request,
                "current_time":datetime.datetime.now()
            }
        
        else:
            context = {
                "error_message": f"Student with id '{student_id}' not found",
            }
       
        pdf = render_to_pdf('pdf/student_transcript.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "%s.pdf" % ("Reports")
            content = "inline; filename='%s'" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")