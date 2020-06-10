from random import sample
from django.db import models
from django.contrib.auth.models import User
from school.models import School
from django.conf import settings
from django.utils import timezone
import time
from sms.tasks import send_bulk_sms
from django.conf import settings


class Staff(models.Model):
    staff_id    = models.CharField(max_length=100, unique=True)
    name        = models.CharField(max_length=100)
    sms_number  = models.CharField(max_length=10)
    has_left    = models.BooleanField(default=False)
    gender      = models.CharField(max_length=10)
    temporal_pin = models.CharField(max_length = 10)
    user        = models.OneToOneField(User, related_name="staff", on_delete=models.CASCADE, null=True, blank=True)
    date        = models.DateTimeField(default = timezone.now)
    activated   = models.BooleanField(default=False)
    image       = models.FileField(upload_to="images/profiles", default="assets/images/avatar.png")
    
    class Meta:
        verbose_name_plural = "Staff"

        
    def get_short_name(self):
        return self.name.split()[0]

    def save(self, *args, **kwargs):
        if not self.user:
            self.temporal_pin = ''.join(sample("0123456789", 5))
            # Strengthen password with secret key
            password = self.temporal_pin + settings.SECRET_KEY
            
            last_name = self.name.split()[0]
            first_name = self.name.split()[1:][0] if self.name.split()[1:] else ""

            user = User.objects.get_or_create(username=self.staff_id)[0]
            
            if user and password:
                user.set_password(password)
                user.last_name = last_name
                user.first_name = first_name
                user.save()
                
                # Map user to student
                self.user = user

                # Send login details to parent
                send_bulk_sms.delay(numbers=self.sms_number, 
                        name = self.name,
                        message=f"Hello {self.name.upper()},  \
                                \nYour login details are: \
                                \nUsername: {self.staff_id} \
                                \nPin: {self.temporal_pin} \
                                \nhttps://idealms.herokuapp.com/accounts/login/\
                                "
                )
        super(Staff, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_full_name(self):
        return self.name
    
    def get_number_of_students(self):
        number = 0
        
        # TODO: Try except
        for teach in self.teaches:
            number += teach.subject.students.all().count()
        return number

