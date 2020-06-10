from django.contrib import admin
from .models import Student, Subject, Course, StudentClass, Record, Teach, ClassTeacherRemarks, HouseMasterRemarks

admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(StudentClass)
admin.site.register(Course)
admin.site.register(Record)
admin.site.register(Teach)
admin.site.register(HouseMasterRemarks)
admin.site.register(ClassTeacherRemarks)
