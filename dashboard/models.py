from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from student.models import Subject, StudentClass
from . functions import timeleft as tl

class UploadedFile(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to="uploads")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(default=timezone.now)
    approved  = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class RecordFile(models.Model):
    name          = models.CharField(max_length=100)
    file          = models.FileField(upload_to="uploads/records")
    academic_year = models.CharField(max_length=100)
    semester      = models.CharField(max_length=50)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    subject       = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL)
    date          = models.DateTimeField(default=timezone.now)
    deadline      = models.DateTimeField(null=True)
    replied       = models.OneToOneField("UploadedFile", related_name="record_file", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Subject Teacher Request"
        verbose_name_plural = "Subject Teacher Requests"
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = "{} - {} {}".format(self.subject.name, self.semester, self.academic_year)
        super(RecordFile, self).save(*args, **kwargs)
    
    def time_left(self):
        return tl(self.deadline)

class HouseMasterRequest(models.Model):
    name          = models.CharField(max_length=100)
    file          = models.FileField(upload_to="uploads/house master")
    academic_year = models.CharField(max_length=100)
    semester      = models.CharField(max_length=50)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    date          = models.DateTimeField(default=timezone.now)
    deadline      = models.DateTimeField(null=True)
    replied       = models.OneToOneField("UploadedFile", related_name="house_master_request", null=True,blank=True, on_delete=models.SET_NULL)
    house         = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = "{} - {} {} Remarks".format(self.academic_year, self.semester, self.student_class.name)
        super(HouseMasterRequest, self).save(*args, **kwargs)
    
    def time_left(self):
        return tl(self.deadline)

class ClassTeacherRequest(models.Model):
    name          = models.CharField(max_length=100)
    file          = models.FileField(upload_to="uploads/house master")
    academic_year = models.CharField(max_length=100)
    semester      = models.CharField(max_length=50)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    date          = models.DateTimeField(default=timezone.now)
    deadline      = models.DateTimeField(null=True)
    replied       = models.OneToOneField("UploadedFile", related_name="class_teacher_request", null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = "{} - {} {} Remarks".format(self.academic_year, self.semester, self.student_class.name)
        super(ClassTeacherRequest, self).save(*args, **kwargs)
    
    def time_left(self):
        return tl(self.deadline)

class PromotionHistory(models.Model):
    old_class    = models.ForeignKey(StudentClass, related_name="old_history",  on_delete=models.CASCADE)
    new_class    = models.ForeignKey(StudentClass, related_name="new_history", on_delete=models.CASCADE)
    date         = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Promotion Histories"