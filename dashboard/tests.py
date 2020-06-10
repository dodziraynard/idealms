from django.test import TestCase
from staff.models import Staff
from student.models import Student, StudentClass, HouseMaster, Record
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.conf import settings
from django.test.client import Client

from . utils import (add_staff,
                    add_students,
                    add_classes,
                    add_subjects,
                    add_courses,
                    add_house_masters,
                    add_record,
                    add_house_master_remarks,
                    add_class_teacher_remarks,
                    map_teacher_subjects)
class TestUserPasswords(TestCase):

    def setUp(self):
        self.staff = Staff.objects.create(
            name = "Kofi Ghana",
            sms_number = "0",
            staff_id = "1111",
            gender = "Male",
        )

        self.student = Student.objects.create(
            name = "Some Student",
            parent_sms = "0",
            student_id = "1000",
            gender = "Male",
        )

    def test_staff_passwords(self):
        password = self.staff.temporal_pin + settings.SECRET_KEY
        user = authenticate(username=self.staff.staff_id, password=password)
        self.assertTrue(user is not None)

    def test_student_passwords(self):
        password = self.student.temporal_pin + settings.SECRET_KEY
        user = authenticate(username=self.student.student_id, password=password)
        self.assertTrue(user is not None)


class TestUploadFunctions(TestCase):
    def setUp(self):
        self.staff_sheet = "dashboard/test_sheets/staff.xlsx"
        self.subject_sheet = "dashboard/test_sheets/subjects.xlsx"
        self.course_sheet = "dashboard/test_sheets/courses.xlsx"
        self.class_sheet = "dashboard/test_sheets/classes.xlsx"
        self.student_sheet = "dashboard/test_sheets/students.xlsx"
        self.teacher_subject_sheet = "dashboard/test_sheets/teacher_subjects.xlsx"
        self.house_master_sheet = "dashboard/test_sheets/house_masters.xlsx"
        self.class_teacher_remark_sheet = "dashboard/test_sheets/class_teacher_remarks.xlsx"
        self.house_master_remark_sheet = "dashboard/test_sheets/house_master_remarks.xlsx"
        self.academic_record_sheet = "dashboard/test_sheets/academic_records.xlsx"
        self.client = Client()

    def test_upload_functions(self):
        response = self.client.get("/")
        request = response.wsgi_request
        
        self.assertTrue(add_staff(request, self.staff_sheet))
        self.assertTrue(add_subjects(request, self.subject_sheet))    
        self.assertTrue(add_courses(request, self.course_sheet))    
        self.assertTrue(add_classes(request, self.class_sheet))
        self.studentclass = StudentClass.objects.first()
        self.assertTrue(add_students(request, self.student_sheet, self.studentclass))    
        self.assertTrue(map_teacher_subjects(request, self.teacher_subject_sheet))        
        self.assertTrue(add_house_masters(request, self.house_master_sheet))    
        self.assertTrue(add_record(request, self.academic_record_sheet))    
        self.assertTrue(add_house_master_remarks(request, self.house_master_remark_sheet))    
        self.assertTrue(add_class_teacher_remarks(request, self.class_teacher_remark_sheet))