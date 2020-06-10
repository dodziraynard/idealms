from django.shortcuts import render, redirect
from .models import School

def update(request):
    if not (request.method == "POST" and request.user.is_authenticated):
        return HttpResonse("Not Accessible", status=403)
    
    referer = request.META.get("HTTP_REFERER")

    current_academic_year = request.POST.get("current_academic_year")
    current_semester = request.POST.get("current_semester")
    sms_id = request.POST.get("sms_id")
    name = request.POST.get("name")

    school = School.objects.get(id=request.school.id)
    school.current_academic_year = current_academic_year
    school.current_semester = current_semester
    school.sms_id = sms_id
    school.name = name
    school.save()

    if referer:
        return redirect(referer)
    return redirect("dashboard:index")