from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from student.models import Student, StudentClass, Record
from staff.models import Staff
from sms.tasks import send_bulk_sms
from lms.celery import get_celery_worker_status
from django.conf import settings
import requests
from .models import FailedSMS
from helpers.functions import redirect_handler, get_numbers
from school.models import School

def check_balance(request):
    school = School.objects.all().first()
    if school:
        key = school.sms_api_key or settings.MNOTIFY_API
    else:
        key = settings.MNOTIFY_API
    url = f"https://apps.mnotify.net/smsapi/balance?key={key}"
    response = requests.get(url)
    return HttpResponse("Balance: <b>{}</b>".format(response.text))

def index(request):
    if request.method == "GET":
        error_message = ""
        message = ""
        if not get_celery_worker_status():
            error_message = "Message broker not working. Please contact the system administrator"
        else:
            message = "Message broker active!"
        classes = StudentClass.objects.all()
        academic_years = Record.objects.all().values("academic_year").distinct()
        semesters = Record.objects.all().values("semester").distinct()
        context = {
            "semesters":semesters,
            "academic_years":academic_years,
            "classes":classes,
            "error_message":error_message,
            "message":message,
            "failedsms":FailedSMS.objects.all().order_by("-date"),
            "sms_status":request.session.pop("sms_status", ""),
        }
        return render(request, "sms/index.html", context)

        # SEND SMS
    elif request.method == "POST":
        academic_year = request.POST.get("academic_year")
        semester = request.POST.get("semester")

        # Report class_id
        class_id = request.POST.get("class_id")
        # Report of those in class:
        student_class = request.POST.get("student_class", "")
        # Formating the posted strings
        ay = "-".join(academic_year.split("/"))
        # if sending for a student
        student_id = request.POST.get("student_id", "")
        if student_id:
            students = Student.objects.filter(student_id = student_id)
    
        # if sending for a class
        elif student_class:
            students = Student.objects.filter(student_class__student_class_id = student_class)
        
        sm = "-".join(semester.split(" "))
        for student in students:
            print(student)
            if request.POST.get(student.student_id):
                student_id = "-".join(student.student_id.split("/"))
                records = Record.objects.filter(student = student, 
                                        record_class__student_class_id = class_id,
                                        semester = semester,
                                        academic_year = academic_year
                                        )
                sms_string = f"{student.name.upper()} ({student.student_id}) \n{academic_year} {semester.upper()} TERMINAL REPORT"
                
                for record in records:
                    sms_string += f"\n {record.subject.name.title()} \t- {record.grade}"
                
                link = f"\n\nLink: {request.scheme}://{request.get_host()}/results/{ay}/{sm}/{student_id}"
                sms_string += link
                send_bulk_sms.delay(message=sms_string, name=student.name, numbers=student.parent_sms)
        return redirect("sms:index")

def actions(request):
    if request.method == "POST":
        failed_ids = request.POST.getlist("failed_ids")
        action = request.POST.get("action")
        print(action)
        if action == "resend":
            return redirect_handler(request, "sms:resend_sms", {"failed_ids":failed_ids})
        
        elif action == "delete":
            failedsms = FailedSMS.objects.filter(id__in=failed_ids)
            context = {
                "failedsms":failedsms
            }
            return render(request, "sms/confirm_delete.html", context)

    else:
        return redirect("sms:index")

# Send general sms
def general(request):
    if request.method =='POST':
        numbers = ""
        message = request.POST.get("message")
        parents = request.POST.get("parents")
        teachers = request.POST.get("teachers")
        entered_numbers = request.POST.get("entered_numbers")

        if parents:
            students = Student.objects.filter(completed=False)
            for student in students:
                numbers += f"{student.parent_sms},"
        
        if teachers:
            teachers = Staff.objects.filter(has_left=False)
            for teacher in teachers:
                numbers += f"{teacher.sms_number},"

        if entered_numbers:
            entered_numbers = entered_numbers.split(",")
            for number in entered_numbers:
                if  number.strip():
                    numbers += f"{number.strip()},"

        excel_file = request.FILES.get("files")
        if excel_file:
            COLUMN_LIMIT = 1
            file_extention = str(excel_file).split(".")[-1]
            if (file_extention == "xls") or file_extention == "xlsx":
                
                file_extention = str(excel_file).split(".")[-1]
                if (file_extention == "xls"):
                    data = xls_get(excel_file, column_limit = COLUMN_LIMIT)
                else:
                    data = xlsx_get(excel_file, column_limit = COLUMN_LIMIT)
                try:
                    contacts = data["sms_contacts"]
                    for row in contacts:
                        if (len(row) > 0):
                            if(row[0].isdigit() and len(row[0])==10):
                                numbers += f"{row[0]},"
    
                except KeyError as err:
                    request.session["error_message"] = f"The uploaded file has no sheet named '{sheet_name}'"
                    return False
            else:
                request.session["error_message"] = "File format not acceptable"
                return redirect("sms:index")
        
        send_bulk_sms.delay(name="bulk", message=message, numbers=numbers)

    return redirect("sms:index")
    

def resend_sms(request):
    ids = get_numbers(request.GET.get("failed_ids"))
    for id in ids:
        sms = get_object_or_404(FailedSMS, pk=id)
        send_bulk_sms.delay(name="bulk", message=sms.message, numbers=sms.number)
        sms.delete()
    return redirect("sms:index")


def delete_sms(request):
    failed_ids = request.POST.getlist("failed_ids")
    for id in failed_ids:
        sms = get_object_or_404(FailedSMS, pk=id)
        sms.delete()
    return redirect("sms:index")

def preview_report(request):
    error_message = ""
    message = ""
    if not get_celery_worker_status():
        error_message = "Message broker not working contact. Please contact the system administrator"
    else:
        message = "Message broker Active!"

    academic_year = request.GET.get("academic_year")
    semester = request.GET.get("semester")
    # Report class_id
    class_id = request.GET.get("class_id", "")
    # Report of those in class:
    student_class = request.GET.get("student_class", "")

    ay = "-".join(academic_year.split("/"))

    # if previewing for a student
    std_id = request.GET.get("student_id", "")
    if std_id:
        students = Student.objects.filter(student_id = std_id)
    
    # if previewing for a class
    elif student_class:
        students = Student.objects.filter(student_class__student_class_id = student_class)
    
    sm = "-".join(semester.split(" "))
    student_sms = {}
    student_link = {}
    for student in students:
        student_id = "-".join(student.student_id.split("/"))
        records = Record.objects.filter(student = student, 
                                record_class__student_class_id = class_id,
                                semester = semester,
                                academic_year = academic_year
                                )

        if records:
            sms_string = f"{student.name.upper()} ({student.student_id}) \n{academic_year} {semester.upper()} TERMINAL REPORT"
            for record in records:
                sms_string += f"\n {record.subject.name.title()} \t- {record.grade}"
            
            link = f"\n\nLink: {request.scheme}://{request.get_host()}/results/{ay}/{sm}/{student_id}"
            sms_string += link
            student_sms.update({student:sms_string})
            student_link.update({student:f"{request.scheme}://{request.get_host()}/results/{ay}/{sm}/{student_id}"})

    context = {
        "student_sms":student_sms,
        "class_id": class_id,
        "student_id": "/".join(std_id.split("-")) if std_id else "",
        "academic_year":academic_year,
        "semester":semester,
        "error_message":error_message,
        "message":message,
        "student_link":student_link,
        "student_class":student_class,
    }
    return render(request, "sms/report_sms_preview.html", context)