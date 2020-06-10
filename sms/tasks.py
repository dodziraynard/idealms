from celery import shared_task
from .models import TaskHistory
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
from datetime import datetime
from .models import FailedSMS, SentSMS
import requests
from requests.exceptions import ConnectionError
from django.conf import settings
from django.utils import timezone
from urllib.parse import urlencode
from school.models import School

logger = get_task_logger(__name__)

def get_sms_credentials():
    school = School.objects.all().first()
    if school:
        key = school.sms_api_key or settings.MNOTIFY_API
        sms_id = school.sms_id or "IDEA LMS"
    else:
        key = settings.MNOTIFY_API
        sms_id = "IDEA LMS"
    return (key, sms_id)

@shared_task
def send_bulk_sms(name, message, numbers):
    if not (numbers and len(numbers) >=10 and message): return
    key, sms_id = get_sms_credentials()
    # Removing trailing comma
    if not numbers[len(numbers)-1].isdigit():
        numbers = numbers[:len(numbers)-1]
    params = {"key":key,"to":numbers,"msg":message,"sender_id":sms_id}
    # {next:"/"}
    query_string = urlencode(params) #?next=?
    url = "https://apps.mnotify.net/smsapi?{}".format(query_string)
    
    response = ""
    reason = ""
    try:
        response = requests.get(url)
        code = response.json().get("code")
        reason =  response.json().get("message")   

        if not (str(code) == str(1000) or reason == "Message submited successful"):
            fs = FailedSMS.objects.get_or_create(
                        message = message,
                        number  = numbers,
                        name    = name,
                    )[0]
            fs.reason  = reason
            fs.code  = code
            fs.save()
        else:
            ss = SentSMS(
                message = message,
                number = numbers,
                name = name,
                code = code,
            )
            ss.save()

    except ConnectionError as err:
        fs = FailedSMS.objects.get_or_create(
                        message = message,
                        number  = numbers,
                        name    = name,    
                    )[0]
        fs.reason  = "Connection Refused"
        fs.save()

    now = datetime.now()
    date_now = now.strftime("%d-%m-%Y %H:%M:%S")
    
    # The name of the Task, use to find the correct TaskHistory object
    name = "send_sms"
    taskhistory = TaskHistory.objects.get_or_create(name=name)[0]
    if response:
        taskhistory.history.update({numbers: f"{response.text} - {date_now}"})
    else:
        taskhistory.history.update({numbers: f"Connection Error  - {date_now}"})
    taskhistory.save()
    return True