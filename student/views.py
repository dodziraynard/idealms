from django.shortcuts import render, redirect
from student.models import Student, StudentClass, ClassTeacherRemarks, HouseMasterRemarks, Record
from django.contrib.auth.models import User


def student_login(request):
    error_message = request.session.pop("error_message", "")
    request.session.pop("user_type", "")
    
    context = {
        "redirect_link" : request.GET.get("next", ""),
        "error_message": error_message,
    }
    return render(request, "student/login.html", context)


def student(request):
    if not request.user.is_authenticated:
        return redirect("student:login")
    try:
        if not request.user.student:
            return redirect("student:login")
    except User.student.RelatedObjectDoesNotExist:
        return redirect("student:login")

    student = request.user.student
    academic_years   = Record.objects.all().values("academic_year").distinct()
    semesters        = Record.objects.all().values("semester").distinct()

    classes = ""
    if student:
        classes     = StudentClass.objects.filter(course = student.student_class.course) 
    context = {
        "academic_years": academic_years,
        "semesters": semesters,
        "classes": classes,
        "student": student,
    }
    return render(request, "student/student.html", context)
    
    
def one_report_preview(request):
    # if request.method == "POST":
    academic_year = request.POST.get("academic_year")
    student = request.POST.get("student")
    semester = request.POST.get("semester")
    student_class_id = request.POST.get("student_class_id")
    
    teacher_remarks = ClassTeacherRemarks.objects.filter(student__student_id=student, 
                                            semester=semester, 
                                            academic_year=academic_year, 
                                            student_class__student_class_id=student_class_id).first()

    house_master_remarks = HouseMasterRemarks.objects.filter(student__student_id=student, 
                                            semester=semester, 
                                            academic_year=academic_year).first()
                                        
    elective_records = Record.objects.filter(semester=semester,
                                            academic_year = academic_year,
                                            record_class__student_class_id = student_class_id,
                                            student__student_id = student,
                                            subject__is_elective = True,
                                        )
    
    core_records = Record.objects.filter(semester=semester,
                                        academic_year = academic_year,
                                        record_class__student_class_id = student_class_id,
                                        student__student_id = student,
                                        subject__is_elective = False,
                                    )
    
    context = {
        "academic_year": academic_year,
        "student": student,
        "semester": semester,
        "elective_records": elective_records,
        "core_records": core_records,
        "teacher_remarks": teacher_remarks, 
        "house_master_remarks": house_master_remarks,
    }
    return render(request, "student/get_report_preview.html", context)
