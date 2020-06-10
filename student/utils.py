from . models import Student


def filter_students(request):
    filters = {}
    if not len(request.GET):
        return {}, {}

    for item, value in request.GET.items():
        if len(value):
            try:
               value = int(value)
            except ValueError:
                pass
            filters.update({item : value})
    if filters:
        students = Student.objects.filter(**filters)
        return students, filters
    else:
        return Student.objects.all(), {}