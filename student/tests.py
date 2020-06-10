from django.test import TestCase
from student.models import Student, Subject, Record, GradingSystem

class TestRecordDetailComputation(TestCase):

    def setUp(self):
        self.student = Student.objects.create(
            name = "Some Student",
            parent_sms = "0",
            student_id = "1000",
            gender = "Male",
        )
        
        self.subject = Subject.objects.create(
            subject_id = "SOME",
            name        = "ICT",
            is_elective = True,
        )

        self.grading_system = GradingSystem.objects.create(
            min_score = 80,
            grade       = "A",
            remark      = "Excellent"
        )

        self.grading_system2 = GradingSystem.objects.create(
            min_score = 70,
            grade       = "B2",
            remark      = "Very Good"
        )

        self.grading_system3 = GradingSystem.objects.create(
            min_score = 60,
            grade       = "B3",
            remark      = "Good"
        )

        self.record = Record.objects.create(
            student = self.student,
            subject = self.subject,
            exam_score = 60,
            class_score = 80,
        )

    def test_record(self):
        self.assertTrue(self.record.grade=="B3")