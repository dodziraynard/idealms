from django.db import models

SEMESTER_CHOICES = (
    ("First Semester", "First Semester"),
    ("Second Semester", "Second Semester"),
)

ACADEMIC_YEAR_CHOICES = (
    ("2019/2020", "2019/2020"),
    ("2020/2021", "2020/2021"),
)

class School(models.Model):
    name                = models.CharField(max_length=500)
    code                = models.CharField(max_length=50)
    sms_id               = models.CharField(verbose_name="SMS Sender ID", max_length=11, null=True, blank=True)
    sms_api_key          = models.CharField(max_length=200, null=True, blank=True)
    crest               = models.FileField(upload_to="uploads/images", default="/assets/images/crest.png")
    current_semester    = models.CharField(max_length=50, default="First Semester", choices=SEMESTER_CHOICES)
    current_academic_year = models.CharField(max_length=20, default="2019/2020", choices=ACADEMIC_YEAR_CHOICES)

    def __str__(self):
        return  self.name