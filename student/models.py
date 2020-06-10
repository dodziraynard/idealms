from django.db import models
from staff.models import Staff
from django.contrib.auth.models import User
from school.models import School
from django.conf import settings
from random import sample
from django.utils import timezone
import time
from sms.tasks import send_bulk_sms

class Student(models.Model):
    student_id      = models.CharField(max_length=100, unique=True)
    name            = models.CharField(max_length=100)
    parent_sms      = models.CharField(max_length=10)
    student_class   = models.ForeignKey("StudentClass", related_name="students", on_delete=models.SET_NULL, null=True, blank=True)
    electives       = models.ManyToManyField("Subject", related_name="students")
    temporal_pin    = models.CharField(max_length = 10)
    gender          = models.CharField(max_length=10)
    activated       = models.BooleanField(default=False)
    house           = models.CharField(max_length=50)
    completed       = models.BooleanField(default=False)
    user            = models.OneToOneField(User, related_name="student", on_delete=models.CASCADE, null=True, blank=True)
    date            = models.DateField(default = timezone.now)
    image           = models.FileField(upload_to="media/images/profiles", default="/assets/images/avatar.png")


    def save(self, *args, **kwargs):
        if not self.user:
            self.temporal_pin = ''.join(sample("0123456789", 5))
            
            # Strengthen password with secret key
            password = self.temporal_pin + settings.SECRET_KEY
            last_name = self.name.split()[0]
            first_name = self.name.split()[1:][0] if self.name.split()[1:] else ""

            user = User.objects.get_or_create(username=self.student_id)[0]
            
            if user and password:
                user.set_password(password)
                user.last_name = last_name
                user.first_name = first_name
                user.save()
                
                # Map user to student
                self.user = user
                # Send login details to parent
                send_bulk_sms.delay(numbers=self.parent_sms, 
                    name =  self.name,
                    message = f"Hello {self.name.upper()},  \
                            \nYour login details are: \
                            \nUsername: {self.student_id} \
                            \nPin: {self.temporal_pin} \
                            \nhttps://idealms.herokuapp.com/accounts/login/ \
                            "
                )
        super(Student, self).save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.name)

class ClassTeacherRemarks(models.Model):
    student         = models.ForeignKey("Student", on_delete=models.CASCADE)
    semester        = models.CharField(max_length=50)
    academic_year   = models.CharField(max_length=50)
    student_class   = models.ForeignKey("StudentClass", on_delete=models.CASCADE)
    attendance      = models.IntegerField(default=0)
    total_attendance = models.IntegerField(default=0)
    attitude        = models.CharField(max_length=100)
    interest        = models.CharField(max_length=100)
    conduct         = models.CharField(max_length=100)
    remark          = models.CharField(max_length=200)
    date            = models.DateField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Class Teacher Remarks"

    def __str__(self):
        return f"{self.student.name} - {self.semester} {self.academic_year}"

class HouseMasterRemarks(models.Model):
    student         = models.ForeignKey("Student", on_delete=models.CASCADE)
    semester        = models.CharField(max_length=50)
    academic_year   = models.CharField(max_length=50)
    remark          = models.CharField(max_length=200)
    date            = models.DateField(default=timezone.now)
    student_class   = models.ForeignKey("StudentClass", on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "House Master Remarks"

    def __str__(self):
        return f"{self.student.name} - {self.semester} {self.academic_year}"


class StudentClass(models.Model):
    student_class_id    = models.CharField(max_length=50, unique=True)
    name                = models.CharField(max_length=50, unique=True)
    class_teacher       = models.OneToOneField(Staff, related_name="student_class", null=True, on_delete=models.SET_NULL)
    form                = models.IntegerField(default=1)
    stream              = models.CharField(max_length=5)
    course              = models.ForeignKey("Course", related_name="student_classes", on_delete=models.CASCADE)
    
    class Meta:
        verbose_name_plural = "Classes"
        verbose_name = "Class"

    def __str__(self):
        return self.name
    
    def get_number_of_students(self):
        return self.students.all().count()

class Course(models.Model):
    course_id   = models.CharField(max_length=50, unique=True)
    name        = models.CharField(max_length = 100, unique=True)
    subjects    = models.ManyToManyField("Subject", related_name="courses")

    def __str__(self):
        return self.name

    def get_number_of_students(self):
        return self.students.all().count()

class Subject(models.Model):
    subject_id     = models.CharField(max_length=50, unique=True)
    name          = models.CharField(max_length=100, unique=True)
    is_elective   = models.BooleanField()

    def __str__(self):
        return self.name    
    
    def get_number_of_students(self):
        return self.students.all().count()

class Record(models.Model):
    student         = models.ForeignKey("Student", on_delete=models.CASCADE)
    exam_score      = models.IntegerField(default=0, blank=True, null=True)
    class_score     = models.IntegerField(default=0, blank=True, null=True)
    total           = models.IntegerField(default=0, blank=True, null=True)
    subject         = models.ForeignKey("Subject", on_delete=models.PROTECT)
    record_class    = models.ForeignKey("StudentClass", on_delete=models.SET_NULL, null=True)
    grade           = models.CharField(max_length=5, blank=True, null=True)
    remark          = models.CharField(max_length=20, blank=True, null=True)
    position        = models.CharField(max_length=5, blank=True, null=True)
    semester        = models.CharField(max_length=50, blank=True, null=True)
    academic_year   = models.CharField(max_length=50, blank=True, null=True)
    date            = models.DateField(default=timezone.now)
    roll_no         = models.IntegerField(blank=True, null=True)
    rank            = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.student.name

    def save(self, *args, **kwargs):
        self.rank = f"{self.position}/{self.roll_no}"
        self.record_class = self.student.student_class
        self.total = round(0.3 * float(self.class_score) + 0.7 * float(self.exam_score))

        grade = GradingSystem.objects.filter(min_score__lte=self.total).order_by("-min_score").first()
        if grade:
            self.grade = grade.grade
            self.remark = grade.remark
        else:
            self.grade = "F"
            self.remark = "Fail"

        super(Record, self).save(*args, **kwargs)


# Subject and the class a teacher teaches
class Teach(models.Model):
    subject = models.ForeignKey("Subject", on_delete=models.CASCADE, related_name="teachers")
    student_class = models.ForeignKey("StudentClass", verbose_name="Class", on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, related_name="teaches", verbose_name="Teacher", null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Subject Assignment to Teachers"
        verbose_name = "Subject Assignment to Teachers"

    def __str__(self):
        if self.subject and self.staff:
            return "{} - {}: {}".format(self.subject.name.capitalize(), self.student_class.name, self.staff.name)
        else:
            return str(self.id)

class HouseMaster(models.Model):
    staff = models.OneToOneField(Staff, related_name="housemaster", on_delete=models.CASCADE)
    house = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        self.house = self.house.title()
        super(HouseMaster, self).save(*args, **kwargs)

    def __str__(self):
        return "{} - {}".format(self.staff.name, self.house)

class GradingSystem(models.Model):
    min_score   = models.IntegerField()
    grade       = models.CharField(max_length=5)
    remark      = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.min_score} - {self.grade} - {self.remark}"