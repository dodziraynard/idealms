from django.contrib import admin
from .models import UploadedFile, RecordFile, HouseMasterRequest, ClassTeacherRequest, PromotionHistory
from student.models import HouseMaster

admin.site.register(UploadedFile)
admin.site.register(RecordFile)
admin.site.register(HouseMaster)
admin.site.register(HouseMasterRequest)
admin.site.register(ClassTeacherRequest)
admin.site.register(PromotionHistory)