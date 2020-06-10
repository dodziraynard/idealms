from django.shortcuts import render
from student.models import GradingSystem
from django.http import JsonResponse


def grading(request):
    systems = GradingSystem.objects.all().order_by("-min_score")
    data = {"grading": list(systems.values())}
    
    return JsonResponse(data)
