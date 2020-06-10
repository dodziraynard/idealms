from django.shortcuts import render, redirect, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from lms import celery
from school.models import School
from staff.models import Staff
from student.models import Student, StudentClass, Subject, Course, HouseMaster, Record, Teach, GradingSystem
from helpers.functions import redirect_handler
from .utils import add_staff, add_students, add_subjects, add_courses, add_classes, add_house_masters, map_teacher_subjects
from .models import UploadedFile, RecordFile, HouseMasterRequest, ClassTeacherRequest, PromotionHistory
from student.utils import filter_students
from datetime import datetime
from django.utils.timezone import make_aware
from accounts.decorators import login_required, logged_in_as
from .tasks import generate_subject_teacher_template


@login_required
def index(request):
    user_type = request.user_type
    # Subject teacher
    if user_type == "teacher":                
        return redirect("staff:input_subject_records")

    elif user_type == "formteacher":                
        return redirect('staff:input_form_master_remarks')

    elif user_type == "housemaster":                
        return redirect('staff:input_house_master_remarks')
    
    # Admin
    else:
        return redirect("dashboard:welcome")


def welcome(request):
    if not request.user.is_superuser:
        request.session["user_not_permitted_error"] = "Access denied!"
        return redirect("accounts:login")
    school = School.objects.all().first()
    context = {
        "school":school,
    }
    return render(request, "dashboard/welcome.html", context)

@login_required
def staff(request):
    # Checking for login
    if not request.user.is_superuser:
        request.session["user_not_permitted_error"] = "Access denied!"
        return redirect("accounts:login")

    if request.method == "GET":
        error_message = request.session.pop('error_message', None)
        staff_id = request.GET.get("staff_id")
        if staff_id:
            staff = Staff.objects.filter(staff_id__icontains=staff_id)
        else:
            staff = Staff.objects.all()
        context = {
            "staff": staff,
            "error_message": error_message,
            "staff_id":staff_id if staff_id else ""
        }
        return render(request, "dashboard/staff.html", context)       

    if request.method == "POST":
        try:
            excel_file = request.FILES["files"]
            file_extention = str(excel_file).split(".")[-1]

            if (file_extention == "xls") or file_extention == "xlsx":
                
                if add_staff(request, excel_file):
                    #    Saving the file 
                    file = UploadedFile.objects.create(user = request.user, file=excel_file, 
                            name=excel_file.name[:len(excel_file.name)-len(file_extention)-1])
            else:
                request.session["error_message"] = "File format not acceptable"
                return redirect("dashboard:staff")
        except MultiValueDictKeyError:
            request.session["error_message"] = "No file selected"
        return redirect("dashboard:staff")

@login_required
def students(request):
    # Checking for login
    if not request.user.is_superuser:
        request.session["user_not_permitted_error"] = "Access denied!"
        return redirect("accounts:login")

    context = {}
    if request.method == "GET":
        error_message = request.session.pop('error_message', None)
        student_id = request.GET.get("student_id", "")
        
        filters = {student_id: student_id}
        if student_id:
            students = Student.objects.filter(student_id__icontains=student_id)
        else:
            students, filters = filter_students(request)
        
        context = {
            "students"      : students,
            "error_message" : error_message,
            "classes"         : StudentClass.objects.all(),
            **filters,
        }
        return render(request, "dashboard/students.html", context)

    if request.method == "POST":
        try:
            excel_file = request.FILES["files"]
            student_class_id = request.POST["student_class"]
            file_extention = str(excel_file).split(".")[-1]

            if (file_extention == "xls") or file_extention == "xlsx":
                student_class = StudentClass.objects.filter(student_class_id=student_class_id).first()
                if student_class:
                    # Saving student
                    if add_students(request, excel_file, student_class):
                         #    Saving the file 
                        file = UploadedFile.objects.create(user = request.user, file=excel_file, 
                                    name=excel_file.name[:len(excel_file.name)-len(file_extention)-1])
                else:
                    request.session["error_message"] = f"Class with ID '{student_class_id}' not found"
                    return redirect("dashboard:students")
            else:
                request.session["error_message"] = "File format not acceptable"
                return redirect("dashboard:students")
        except MultiValueDictKeyError:
            request.session["error_message"] = "No file selected"
        return redirect("dashboard:students")       

@login_required
def student_reports(request):
    if not request.user.is_superuser:
        request.session["user_not_permitted_error"] = "Access denied!"
        return redirect("accounts:login")
    academic_years   = Record.objects.all().values("academic_year").distinct()
    semesters        = Record.objects.all().values("semester").distinct()

    context = {
        "academic_years": academic_years,
        "semesters": semesters,
        "classes": StudentClass.objects.all(),
    }
    return render(request, "dashboard/student_reports.html", context)


@login_required
def transcript(request):
    if not request.user.is_superuser:
        request.session["user_not_permitted_error"] = "Access denied!"
        return redirect("accounts:login")

    context = {
        "classes": StudentClass.objects.all(),
    }
    return render(request, "dashboard/transcript.html", context)


@login_required
def student_classes(request):
    # Checking for login
    if not request.user.is_superuser:
        request.session["user_not_permitted_error"] = "Access denied!"
        return redirect("accounts:login")

    context = {}
    if request.method == "GET":
        # Get error from posting
        error_message = request.session.pop('error_message', None)
        student_class_id = request.GET.get("student_class_id")
        if student_class_id:
            student_classes = StudentClass.objects.filter(student_class_id__icontains=student_class_id)
        else:
            student_classes = StudentClass.objects.all()
        context = {
            "student_classes": student_classes,
            "error_message": error_message,
            "student_class_id":student_class_id if student_class_id else ""
        }
        return render(request, "dashboard/student_classes.html", context)

    if request.method == "POST":
        try:
            excel_file = request.FILES["files"]
            file_extention = str(excel_file).split(".")[-1]

            if (file_extention == "xls") or file_extention == "xlsx":
                if add_classes(request, excel_file):
                    #    Saving the file 
                    file = UploadedFile.objects.create(user = request.user, file=excel_file, 
                            name=excel_file.name[:len(excel_file.name)-len(file_extention)-1])
                
            else:
                request.session["error_message"] = "File format not acceptable"
                return redirect("dashboard:student_classes")
        except MultiValueDictKeyError:
            request.session["error_message"] = "No file selected"
        return redirect("dashboard:student_classes")       

@login_required
def subjects(request):
    # Checking for login
    if not request.user.is_superuser:
        request.session["user_not_permitted_error"] = "Access denied!"
        return redirect("accounts:login")

    context = {}
    if request.method == "GET":
        error_message = request.session.pop('error_message', None)
        subject_id = request.GET.get("subject_id")
        if subject_id:
            subjects = Subject.objects.filter(subject_id__icontains=subject_id)
        else:
            subjects = Subject.objects.all()
        context = {
            "subjects": subjects,
            "error_message": error_message,
            "subject_id":subject_id if subject_id else ""
        }
        return render(request, "dashboard/subjects.html", context)

    if request.method == "POST":
        try:
            excel_file = request.FILES["files"]
            file_extention = str(excel_file).split(".")[-1]

            if (file_extention == "xls") or file_extention == "xlsx":
                
                if  add_subjects(request, excel_file):
                    #    Saving the file 
                    file = UploadedFile.objects.create(user = request.user, file=excel_file, 
                        name=excel_file.name[:len(excel_file.name)-len(file_extention)-1])
                
                return redirect("dashboard:subjects")
            else:
                request.session["error_message"] = "File format not acceptable"
                return redirect("dashboard:subjects")
        except MultiValueDictKeyError:
            request.session["error_message"] = "No file selected"
        return redirect("dashboard:subjects") 

@login_required
def courses(request):
    # Checking for login
    if not request.user.is_superuser:
        request.session["user_not_permitted_error"] = "Access denied!"
        return redirect("accounts:login")

    if request.method == "GET":
        error_message = request.session.pop('error_message', None)
        course_id = request.GET.get("course_id")
        if course_id:
            courses = Course.objects.filter(course_id__icontains=course_id)
        else:
            courses = Course.objects.all()
        context = {
            "courses": courses,
            "error_message": error_message,
            "course_id":course_id if course_id else ""
        }
        return render(request, "dashboard/courses.html", context)

    if request.method == "POST":
        try:
            excel_file = request.FILES["files"]
            file_extention = str(excel_file).split(".")[-1]

            if (file_extention == "xls") or file_extention == "xlsx":
                if add_courses(request, excel_file):
                    #    Saving the file 
                    file = UploadedFile.objects.create(user = request.user, file=excel_file, 
                        name=excel_file.name[:len(excel_file.name)-len(file_extention)-1])
            else:
                request.session["error_message"] = "File format not acceptable"
                return redirect("dashboard:courses")
        except MultiValueDictKeyError:
            request.session["error_message"] = "No file selected"
        return redirect("dashboard:courses") 

@login_required
def files(request):
    # Checking for login
    if not request.user.is_superuser:
        request.session["user_not_permitted_error"] = "Access denied!"
        return redirect("accounts:login")

    files = UploadedFile.objects.all().order_by("-date")
    file_name = request.GET.get("file_name")
    if file_name:
        files = files.filter(name__icontains=file_name)
    return render(request, "dashboard/files.html", {"files":files})

@login_required
def records(request):
    # Checking for login
    if not request.user.is_superuser:
        request.session["user_not_permitted_error"] = "Access denied!"
        return redirect("accounts:login")
    # If user searches
    if request.method == "GET":
        query = request.GET.get("name__icontains", "")
        if query:
            records = RecordFile.objects.filter(name__icontains=query).order_by("-date")[:10]
            class_teacher_request = ClassTeacherRequest.objects.filter(name__icontains=query).order_by("-date")[:10]
            house_master_request = HouseMasterRequest.objects.filter(name__icontains=query).order_by("-date")[:10]
        else: 
            records = RecordFile.objects.all().order_by("-date")[:10]
            class_teacher_request = ClassTeacherRequest.objects.all().order_by("-date")[:10]
            house_master_request = HouseMasterRequest.objects.all().order_by("-date")[:10]
        
        subjects = Subject.objects.all()
        error_message = request.session.pop("error_message", "") #From previous activity
        context = {
            "subjects":subjects,
            "class_teacher_request" : class_teacher_request,
            "house_master_request"  : house_master_request,
            "masters"  : HouseMaster.objects.all().distinct().values("house"),
            "records": records,
            "error_message": error_message,
            "student_classes": StudentClass.objects.all(),
        }
        return render(request, "dashboard/records.html", context)

    elif request.method == "POST":
        subject_id          = request.POST.get("subject")
        semester            = request.POST.get("semester")
        student_class_id    = request.POST.get("student_class")
        academic_year       = request.POST.get("academic_year")
        file                = request.FILES.get("file")
        deadline            = request.POST.get("deadline")

        # Add timezone info
        try:
            deadline = make_aware(datetime.strptime(deadline, '%Y-%m-%dT%H:%M'))
        except ValueError as err:
            request.session["error_message"] = f"Invalid deadline date format. {str(err)}"
            return redirect("dashboard:records")
            
        file_extention = str(file).split(".")[-1]
        if (file_extention != "xls") and file_extention != "xlsx":
            request.session["error_message"] ="An excel file is required"
            return redirect("dashboard:records")

        elif subject_id and semester and academic_year and file and deadline:
            subject = Subject.objects.get(subject_id=subject_id)
            student_class = StudentClass.objects.get(student_class_id=student_class_id)
            record_file = RecordFile(subject=subject,
                                        semester = semester,
                                        academic_year = academic_year,
                                        file        =  file, 
                                        student_class = student_class,
                                        deadline = deadline
                                    )
            record_file.save()
            return redirect("dashboard:records")
            records = RecordFile.objects.all().order_by("-date")
        else:
            request.session["error_message"] = "All fields are required"
            return redirect("dashboard:records")

@login_required
def house_masters(request):
    # Checking for login
    if not request.user.is_superuser:
        request.session["user_not_permitted_error"] = "Access denied!"
        return redirect("accounts:login")

    if request.method == "GET":
        staff_id = request.GET.get("staff_id", "")
        if staff_id:
            house_masters = HouseMaster.objects.filter(staff__staff_id__icontains=staff_id)
        else:
            house_masters = HouseMaster.objects.all()
        
        error_message = request.session.pop('error_message', None)
        context = {
            "house_masters": house_masters,
            "error_message": error_message,
            "staff_id":staff_id
        }
        return render(request, "dashboard/house_masters.html", context)

    elif request.method == "POST":
        try:
            excel_file = request.FILES["files"]
            file_extention = str(excel_file).split(".")[-1]

            if (file_extention == "xls") or file_extention == "xlsx":
                if add_house_masters(request, excel_file):
                    #    Saving the file 
                    file = UploadedFile.objects.create(user = request.user, file=excel_file, 
                            name=excel_file.name[:len(excel_file.name)-len(file_extention)-1])
            else:
                request.session["error_message"] = "File format not acceptable"
                return redirect("dashboard:house_masters")

        except MultiValueDictKeyError:
            request.session["error_message"] = "No file selected"
        return redirect("dashboard:house_masters")       

# Assign subjects to teachers
@login_required
def teacher_subjects(request):
    # Checking for login
    if not request.user.is_superuser:
        request.session["user_not_permitted_error"] = "Access denied!"
        return redirect("accounts:login")
    
    if request.method == "GET":
        error_message = request.session.pop("error_message", "")
        teaches = Teach.objects.all()
        
        # Generate the sheet
        generate_subject_teacher_template()
        
        # Excel sheet template
        teacher_subject = UploadedFile.objects.filter(name="teacher_subjects").order_by("-id").first()
        context = {
            "error_message":error_message,
            "teaches":teaches,
            "teacher_subject":teacher_subject,
        }
        return render(request, "dashboard/teacher_subjects.html", context)
    elif request.method == "POST":
        try:
            excel_file = request.FILES["files"]
            file_extention = str(excel_file).split(".")[-1]

            if (file_extention == "xls") or file_extention == "xlsx":
                if map_teacher_subjects(request, excel_file):
                    #    Saving the file 
                    file = UploadedFile.objects.create(user = request.user, file=excel_file, 
                            name=excel_file.name[:len(excel_file.name)-len(file_extention)-1])
            else:
                request.session["error_message"] = "File format not acceptable"
                return redirect("dashboard:teacher_subjects")

        except MultiValueDictKeyError:
            request.session["error_message"] = "No file selected"
        return redirect("dashboard:teacher_subjects") 

@login_required
def grading_system(request):
    # Checking for login
    if not request.user.is_superuser:
        request.session["user_not_permitted_error"] = "Access denied!"
        return redirect("accounts:login")

    if request.method == "GET":
        gradings = GradingSystem.objects.all()
        error_message = request.session.pop("error_message", "")

        context = {
           "gradings":gradings,
           "error_message":error_message
        }
        return render(request, "dashboard/grading.html", context)

    elif request.method == "POST":
        min_score = request.POST.get("min_score")
        grade = request.POST.get("grade")
        remark = request.POST.get("remark")

        try:
            new_grading = GradingSystem.objects.get_or_create(min_score=min_score)[0]
            new_grading.grade = grade
            new_grading.remark = remark
            new_grading.save()
        except Exception as err:
            request.session["error_message"] = str(err)
        return redirect("dashboard:grading_system")       

def delete_grading_system(request):
    if request.method == "POST":
        grading_id = request.POST.get("grading_id")
        GradingSystem.objects.filter(id=grading_id).delete()
        
    return redirect("dashboard:grading_system")       


# Uploads
@login_required
def upload_class_teacher_sheet(request):
    if request.method == "POST":
        semester            = request.POST.get("semester")
        student_class_id    = request.POST.get("student_class")
        academic_year       = request.POST.get("academic_year")
        file                = request.FILES.get("file")
        deadline            = request.POST.get("deadline")

        # Add timezone info
        try:
            deadline = make_aware(datetime.strptime(deadline, '%Y-%m-%dT%H:%M'))
        except ValueError as err:
            request.session["error_message"] = f"Invalid deadline date format. {str(err)}"
            return redirect("dashboard:records")
            
        file_extention = str(file).split(".")[-1]
        if (file_extention != "xls") and file_extention != "xlsx":
            error_message = "An excel file is required"
            return redirect("dashboard:records")

        elif semester and academic_year and file and deadline:
            student_class = StudentClass.objects.get(student_class_id=student_class_id)
            new_request = ClassTeacherRequest(
                            student_class=student_class,
                            academic_year = academic_year,
                            deadline = deadline,
                            semester = semester,
                            file = file,
                        )
            new_request.save()
            request.session["message"] = "Request made successfully"
    return redirect("dashboard:records")

@login_required
def upload_house_master_sheet(request):
    if request.method == "POST":
        semester            = request.POST.get("semester")
        house            = request.POST.get("house")
        student_class_id    = request.POST.get("student_class")
        academic_year       = request.POST.get("academic_year")
        file                = request.FILES.get("file")
        deadline            = request.POST.get("deadline")

        # Add timezone info
        try:
            deadline = make_aware(datetime.strptime(deadline, '%Y-%m-%dT%H:%M'))
        except ValueError as err:
            request.session["error_message"] = f"Invalid deadline date format. {str(err)}"
            return redirect("dashboard:records")
            
        file_extention = str(file).split(".")[-1]
        if (file_extention != "xls") and file_extention != "xlsx":
            error_message = "An excel file is required"
            return redirect("dashboard:records")

        elif semester and academic_year and file and deadline:
            student_class = StudentClass.objects.get(student_class_id=student_class_id)
            new_request = HouseMasterRequest(
                            student_class=student_class,
                            academic_year = academic_year,
                            deadline = deadline,
                            semester = semester,
                            file = file,
                            house = house
                        )
            new_request.save()
            request.session["message"] = "Request made successfully"
    return redirect("dashboard:records")

def profile(request):
    
    context = {

    }
    return render(request, "dashboard/profile.html", context)

@login_required
def promotion(request):
     # Checking for login
    if not request.user.is_superuser:
        request.session["user_not_permitted_error"] = "Access denied!"
        return redirect("accounts:login")

    if request.method == "GET":
        classes = StudentClass.objects.all().order_by("-form")
        
        # Classes and the posible classes to promote to
        class_classes = {}
        promotion_history = PromotionHistory.objects.all().order_by("-date")[:30]
        for item in classes:
            next_classes = StudentClass.objects.filter(course=item.course)
            class_classes.update({item:next_classes})
            
        context = {
            "class_classes":class_classes,
            "promotion_history":promotion_history,
        }
        return render(request, "dashboard/promotion.html", context)
    if request.method == "POST":
        classes = StudentClass.objects.all()
        for c in classes:
            class_name = request.POST.get(c.name)
            if class_name == "completed":
                Student.objects.filter(student_class=c).update(student_class=None, completed=True)
            else:
                new_class = StudentClass.objects.filter(name=class_name).first()
                if new_class and not c == new_class:
                    students = Student.objects.filter(student_class=c).update(student_class=new_class)
                    PromotionHistory.objects.create(old_class=c, new_class=new_class)
        return redirect("dashboard:promotion")