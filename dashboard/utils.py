from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get
from staff.models import Staff
from student.models import (Student, StudentClass, 
                            Subject, Course, Record, 
                            HouseMaster, ClassTeacherRemarks, 
                            HouseMasterRemarks, Teach)
from django.core.exceptions import FieldError
from django.db.utils import IntegrityError
from .tasks import generate_subject_teacher_template


def _get_data_from_sheet(request, excel_file, COLUMN_LIMIT, sheet_name):
    try:
        file_extention = str(excel_file).split(".")[-1]
        if (file_extention == "xls"):
            data = xls_get(excel_file, column_limit = COLUMN_LIMIT)
        else:
            data = xlsx_get(excel_file, column_limit = COLUMN_LIMIT)
    except Exception as err:
        request.session["error_message"] = str(err)
        return False
    try:
        data = data[sheet_name]
        return data
    except KeyError as err:
        request.session["error_message"] = f"The uploaded file has no sheet named '{sheet_name}'"
        return False
    except Exception as err:
        request.session["error_message"] = str(err)
        return False

# Add Staff to the database
def add_staff(request, excel_file):
    COLUMN_LIMIT = 4
    sheet_name = "staff"
    staff = _get_data_from_sheet(request, excel_file, COLUMN_LIMIT, sheet_name)
    if not staff: return False

    # DATA HEAD FROM SHEET: 
    # No	staff_id	name	sms_number

    # Add teacher to the database
    for row in staff:
        if (len(row) > 0):
            if(row[0] != "No"):
                # if there are empty colums
                if(len(row) < COLUMN_LIMIT): 
                    i = len(row)
                    while (i <  COLUMN_LIMIT):
                        # fill with ""
                        row.append("")
                        i += 1
                try:
                    # Check for the exitence of the staff id
                    t = Staff.objects.filter(staff_id=row[1])
                    if(t.count()==0):
                        new_row = Staff(
                            staff_id    = row[1],
                            name        = row[2],
                            sms_number  = row[3],
                        )
                        new_row.save()
                except ValueError as err:
                    request.session["error_message"] = str(err)
                    return False
                except IntegrityError as err:
                    request.session["error_message"] = str(err)
                    return False
                except FieldError as err:
                    request.session["error_message"] = str(err)
                    return False
                except Exception as err:
                    request.session["error_message"] = str(err)
                    return False
    return True
    
# Add Student to the database
def add_students(request, excel_file, student_class):
    COLUMN_LIMIT = 6
    sheet_name = "students"
    students = _get_data_from_sheet(request, excel_file, COLUMN_LIMIT, sheet_name)
    if not students: return False

    # DATA HEAD FROM EXCEL SHEET: 
    # No	student_id	name	paren_sms	Class ID	course ID	elective IDs

    # Add student to the database
    for row in students:
        if (len(row) > 0):
            if(row[0] != "No" and row[0] !="CLASS ID"):

                # if there are empty colums
                if(len(row) < COLUMN_LIMIT): 
                    i = len(row)
                    while (i <  COLUMN_LIMIT):
                        # fill with ""
                        row.append("")
                        i += 1
                try:
                    # Check for the exitence of the staff id
                    s = Student.objects.filter(student_id=row[1])
                    if(s.count() == 0):
                        # Students elective subjects
                        elective_ids = row[4].split(" ")

                        new_student = Student(
                            student_id      = row[1],
                            name            = row[2],
                            parent_sms      = row[3],
                            student_class   = student_class,
                            house           = row[5].capitalize()
                        )
                        new_student.save()
                        for id in elective_ids:
                            if id:
                                elective = Subject.objects.filter(is_elective=True, subject_id=id).first()
                                if elective:
                                    new_student.electives.add(elective)
                                    new_student.save()
                                else:
                                    new_student.delete()
                                    request.session["error_message"] = f"Elective subject with ID '{id}' not found"
                                    return False
                    else:
                        request.session["error_message"] = "Student IDs must be unique for all students."
                except Exception as err:
                    request.session["error_message"] = str(err)
                    return False
    return True

#  Add StudentClass to the database
def add_classes(request, excel_file):
    COLUMN_LIMIT = 7
    sheet_name = "classes"
    student_classes = _get_data_from_sheet(request, excel_file, COLUMN_LIMIT, sheet_name)
    if not student_classes: return

    # DATA HEAD FROM EXCEL SHEET: 
    # No	CLASS ID	NAME	COURSE ID	Form Master (Staff ID)	form	stream

    # Add student_class to the database

    # Reset form master for all class
    # to enable updates
    StudentClass.objects.all().update(class_teacher=None)

    for row in student_classes:
        if (len(row) > 0):
            if(row[0] != "No"):
                # if there are empty colums
                if(len(row) < COLUMN_LIMIT): 
                    i = len(row)
                    while (i <  COLUMN_LIMIT):
                        # fill with ""
                        row.append("")
                        i += 1
                try:                   
                    # Check for the exitence of the staff id
                    clazz = StudentClass.objects.filter(student_class_id=row[1]).first()
                    teacher = Staff.objects.filter(staff_id=row[4]).first()
                    course = Course.objects.filter(course_id=row[3]).first()

                    if not clazz:
                        if teacher and course:
                            try:
                                if teacher.student_class:
                                    request.session["error_message"] = "Teacher is already a form master"
                                    return False
                            except Staff.student_class.RelatedObjectDoesNotExist:
                                new_form = StudentClass(
                                    student_class_id  = row[1],
                                    name  = row[2],
                                    class_teacher = teacher,
                                    form = row[5],
                                    stream = row[6],
                                    course = course
                                )
                                new_form.save()
                        elif not teacher:
                            request.session["error_message"] = f"Staff with ID '{row[4]}' not found"
                        else:
                            request.session["error_message"] = f"Course with ID '{row[3]}' not found"
                    else:
                        clazz.class_teacher = teacher
                        clazz.course = course
                        clazz.name =  row[2]
                        clazz.form = row[5]
                        clazz.save()

                except ValueError as err:
                    request.session["error_message"] = str(err)
                    return False
                except FieldError as err:
                    request.session["error_message"] = str(err)
                    return False
                except Exception as err:
                    request.session["error_message"] = str(err)
                    return False
    generate_subject_teacher_template()
    return True

#  Add Subject to the database
def add_subjects(request, excel_file):
    COLUMN_LIMIT = 4
    sheet_name = "subjects"
    subjects = _get_data_from_sheet(request, excel_file, COLUMN_LIMIT, sheet_name)
    if not subjects: return False

    # DATA HEAD FROM EXCEL SHEET: 
    # No	Subject ID	NAME	Staff (ID)	is_Elective (Y/N)

    # Add student_class to the database
    for row in subjects:
        if (len(row) > 0):
            if(row[0] != "No"):

                # if there are empty colums
                if(len(row) < COLUMN_LIMIT): 
                    i = len(row)
                    while (i <  COLUMN_LIMIT):
                        # fill with ""
                        row.append("")
                        i += 1
                try:
                    # Check for the exitence of the staff id
                    s = Subject.objects.filter(subject_id=row[1])
                    if(s.count() == 0):
                        is_elective = True if 'y' in row[3] else False
                        new_subject = Subject(
                            subject_id  = row[1],
                            name        = row[2],
                            is_elective = is_elective
                        )
                        new_subject.save()
                except IntegrityError as err:
                    request.session["error_message"] = str(err)
                    return False
                except ValueError as err:
                    request.session["error_message"] = str(err)
                    return False
                except FieldError as err:
                    request.session["error_message"] = str(err)
                    return False
                except Exception as err:
                    request.session["error_message"] = str(err)
                    return False
    generate_subject_teacher_template()
    return True

# Add Courses to the database
def add_courses(request, excel_file):
    COLUMN_LIMIT = 6
    sheet_name = "courses"
    courses = _get_data_from_sheet(request, excel_file, COLUMN_LIMIT, sheet_name)
    if not courses: return False

    # DATA HEAD FROM EXCEL SHEET: 
    # No	Course ID	NAME	Subjects (IDs Separated by comma)

    # Add student_class to the database
    for row in courses:
        if (len(row) > 0):
            if(row[0] != "No"):

                # if there are empty columns
                if(len(row) < COLUMN_LIMIT): 
                    i = len(row)
                    while (i <  COLUMN_LIMIT):
                        # fill with ""
                        row.append("")
                        i += 1
                try:
                    # Check for the exitence of the row id
                    new_course = Course.objects.get_or_create(course_id  = row[1],
                                                         name  = row[2])[0]
                    subject_ids = row[3].split(" ")
                    new_course.subjects.clear()
                    for id in subject_ids:
                        if id:
                            subject = Subject.objects.filter(subject_id=id).first()
                            if subject:
                                new_course.subjects.add(subject)
                                new_course.save()
                            else:
                                new_course.delete()
                                request.session["error_message"] = f"Subject with the ID '{id}' not found"
                                return False
                except IntegrityError as err:
                    request.session["error_message"] = str(err)
                    return False
                except ValueError as err:
                    request.session["error_message"] = str(err)
                    return False
                except FieldError as err:
                    request.session["error_message"] = str(err)
                    return False
                except Exception as err:
                    request.session["error_message"] = str(err)
                    return False
    return True

# Add House masters
def add_house_masters(request, excel_file):
    COLUMN_LIMIT = 4
    sheet_name = "house_masters"
    house_masters = _get_data_from_sheet(request, excel_file, COLUMN_LIMIT, sheet_name)
    if not house_masters: return False

    # DATA HEAD FROM EXCEL SHEET: 
    # No	staff_id	name	house

    # Add house master to the database
    row_start = 1
    for i in range(row_start, len(house_masters)):
        row = house_masters[row_start]
        if (len(row) > 0):    
            if(row[0] != "No"):
                # if there are empty colums
                if(len(row) < COLUMN_LIMIT): 
                    i = len(row)
                    while (i <  COLUMN_LIMIT):
                        # fill with ""
                        row.append("")
                        i += 1
                try:
                    if not row[1]: continue
                    # Check for the exitence of the staff id
                    staff = Staff.objects.filter(staff_id=row[1]).first()
                    if staff:
                        try:
                            if staff.housemaster:
                                request.session["error_message"] = "Teacher already a house master"
                                return False
                        except Staff.housemaster.RelatedObjectDoesNotExist:
                            m = HouseMaster.objects.filter(staff=staff)
                            if(m.count() == 0):
                                new_master = HouseMaster(
                                    staff = staff,
                                    house  = row[3]
                                )
                                new_master.save()
                    else:
                       request.session["error_message"] = f"Staff with ID '{row[1]}' not found"
                       return False
                except ValueError as err:
                    request.session["error_message"] = str(err)
                    return False
                except FieldError as err:
                    request.session["error_message"] = str(err)
                    return False
                except Exception as err:
                    request.session["error_message"] = str(err)
                    return False
        row_start += 1
    return True

# Add record
def add_record(request, excel_file):
    COLUMN_LIMIT = 5
    sheet_name = "records"
    records = _get_data_from_sheet(request, excel_file, COLUMN_LIMIT, sheet_name)
    if not records: return False

    # DATA HEAD FROM EXCEL SHEET: 
    # STUDENT ID	STUDENT NAME	CLASS SCORE	EXAM SCORE	TOTAL	GRADE	REMARK 	POSITION 
    
    # Add student_class to the database
    roll_no         = records[14][1]
    academic_year   = records[15][1]
    subject_name    = records[17][1]
    semester        = records[18][1]

    subject = Subject.objects.filter(name=subject_name).first()
    if not subject:
        request.session["error_message"] = f"Subject with the name {subject_name} not found"
        return False

    if not (roll_no and academic_year and subject_name and semester):
        request.session["error_message"] = "Please fill the cell for No. on Roll, Academic Year, Class ID, Subject and Semester"
        return False

    row_start = 21

    # Gather marks to find position
    totals  = []
    for i in range(row_start, len(records)):
        row = records[row_start]
        if (len(row) > 0):           
            # if there are empty columns
            if(len(row) < COLUMN_LIMIT): 
                i = len(row)
                while (i <  COLUMN_LIMIT):
                    # fill with ""
                    row.append("")
                    i += 1

            student = Student.objects.filter(student_id=row[0]).first()
            total = round(0.3 * row[2] + 0.7 * row[3])
            totals.append(total)
        row_start += 1
    # Sort records
    totals= sorted(totals, reverse=True)

    row_start = 21
    for i in range(row_start, len(records)):
        row = records[row_start]
        if (len(row) > 0):           
            # if there are empty columns
            if(len(row) < COLUMN_LIMIT): 
                i = len(row)
                while (i <  COLUMN_LIMIT):
                    # fill with ""
                    row.append("")
                    i += 1
            student = Student.objects.filter(student_id=row[0]).first()
            if student:
                try:
                    # Check for the exitence of the row id
                    r = Record.objects.get_or_create(
                                        student = student, 
                                        record_class=student.student_class,
                                        semester=semester,
                                        subject = subject,
                                        academic_year = academic_year)
                                        
                    new_record = r[0]
                    new_record.class_score= row[2]
                    new_record.exam_score= row[3]
                    new_record.position = totals.index(round(0.3 * row[2] + 0.7 * row[3])) + 1
                    new_record.roll_no = roll_no
                    new_record.save()
                    
                    if r[1]:
                        request.session["message"] = "Records have been added successfully"
                    else:
                        request.session["message"] = "Records updated successfully."            
                except ValueError as err:
                    request.session["error_message"] = str(err)
                    return False
                except FieldError as err:
                    request.session["error_message"] = str(err)
                    return False
                except Exception as err:
                    request.session["error_message"] = str(err)
                    return False
            else:
                request.session["error_message"] = f"Student with ID '{row[0]}' not found"
                return False
        row_start += 1
    return True

# Add house master remarks
def add_house_master_remarks(request, excel_file):
    COLUMN_LIMIT = 3
    sheet_name = "house_master_remarks"
    remarks = _get_data_from_sheet(request, excel_file, COLUMN_LIMIT, sheet_name)
    if not remarks: return False

    academic_year   = remarks[15][1]
    semester        = remarks[16][1]

    # Add remark to the database
    row_start = 18
    for i in range(row_start, len(remarks)):
        row = remarks[row_start]
        if (len(row) > 0):           
            # if there are empty columns
            if(len(row) < COLUMN_LIMIT): 
                i = len(row)
                while (i <  COLUMN_LIMIT):
                    # fill with ""
                    row.append("")
                    i += 1
            try:
                # Check for the exitence of the remark id
                student = Student.objects.get(student_id=row[0])
                r = HouseMasterRemarks.objects.get_or_create(student=student, 
                                    academic_year=academic_year,
                                    semester=semester)
                new_record = r[0]
                new_record.remark = row[2]
                new_record.save()
                
                if r[1]:
                    request.session["message"] = "Records have been added successfully."
                else:
                    request.session["message"] = "Records have been updated."
            except ValueError as err:
                request.session["error_message"] = str(err)
                return False
            except FieldError as err:
                request.session["error_message"] = str(err)
                return False
            except Exception as err:
                request.session["error_message"] = str(err)
                return False
    return True

# Add class teacher remarks
def add_class_teacher_remarks(request, excel_file):
    COLUMN_LIMIT = 7
    sheet_name = "class_teacher_remarks"
    remarks = _get_data_from_sheet(request, excel_file, COLUMN_LIMIT, sheet_name)
    if not remarks: return False

    # DATA ROW FROM EXCEL SHEET: 
    # Student ID	Name	remark

    try:
        class_name = remarks[14][1]
        student_class = StudentClass.objects.filter(name=class_name).first()
        if not student_class:
            request.session["error_message"] = f"Class with name '{class_name} not found"
            return False

        academic_year = remarks[15][1]
        semester = remarks[16][1]
        total_attendance = remarks[17][1]
    except ValueError as err:
        request.session["error_message"] = str(err)
        return False

    # Add remark to the database
    row_start = 19
    for i in range(row_start, len(remarks)):
        row = remarks[row_start]
        if (len(row) > 0):           
            # if there are empty columns
            if(len(row) < COLUMN_LIMIT): 
                i = len(row)
                while (i <  COLUMN_LIMIT):
                    # fill with ""
                    row.append("")
                    i += 1
            try:
                # Check for the exitence of the remark id
                r = ClassTeacherRemarks.objects.filter(student__student_id=row[0], 
                                    academic_year=academic_year,
                                    semester=semester)
                if(r.count() == 0):
                    student = Student.objects.get(student_id=row[0])
                    new_record = ClassTeacherRemarks(
                        student = student,
                        semester = semester,
                        student_class = student_class,
                        academic_year = academic_year,
                        attendance = row[2],
                        total_attendance = total_attendance,
                        attitude    = row[3],
                        interest    = row[4],
                        conduct     = row[5],
                        remark      = row[6]
                    )
                    new_record.save()
                    request.session["message"] = "Records have been added successfully"
                else:
                    request.session["message"] = "No updates, remark alredy exists."
            except ValueError as err:
                request.session["error_message"] = str(err)
                return False
            except FieldError as err:
                request.session["error_message"] = str(err)
                return False
            except Exception as err:
                request.session["error_message"] = str(err)
                return False
        row_start += 1
    return True

# Map teacher to subjects and classes
def map_teacher_subjects(request, excel_file):
    COLUMN_LIMIT = 3
    sheet_name = "teacher_subjects"
    combination = _get_data_from_sheet(request, excel_file, COLUMN_LIMIT, sheet_name)
    if not combination: return False

    # DATA HEAD FROM EXCEL SHEET: 
    # subject	class	staff Id

    row_start = 15
    for i in range(row_start, len(combination)):
        row = combination[row_start]
        if (len(row) > 0):
            # if there are empty colums
            if(len(row) < COLUMN_LIMIT): 
                i = len(row)
                while (i <  COLUMN_LIMIT):
                    # fill with ""
                    row.append("")
                    i += 1
            try:
                # Check for the exitence of the staff id
                if not row[2]: 
                    continue
                staff = Staff.objects.filter(staff_id=row[2]).first()
                clazz = StudentClass.objects.filter(name=row[1]).first()
                subject = Subject.objects.filter(name=row[0]).first()

                if staff and clazz and subject:
                    comb = Teach.objects.get_or_create(subject=subject, student_class=clazz)[0]
                    comb.staff=staff
                    comb.save()

                elif not staff:
                    request.session["error_message"] = f" Staff with ID '{row[2]}' not found"
                    return False
                elif not clazz:
                    request.session["error_message"] = f" Class with name '{row[1]}' not found"
                    return False
                elif not subject:
                    request.session["error_message"] = f" Subject with name '{row[0]}' not found"
                    return False
            except ValueError as err:
                request.session["error_message"] = str(err)
                return False
            except FieldError as err:
                request.session["error_message"] = str(err)
                return False
            except Exception as err:
                request.session["error_message"] = str(err)
                return False
        row_start += 1
    return True