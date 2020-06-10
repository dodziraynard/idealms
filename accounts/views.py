from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from student.models import HouseMaster, StudentClass
from staff.models import Staff

# Login
class Login(View):
    template_name = 'accounts/login.html'
    
    # Display blank form
    def get(self, request):
        error_message = request.session.pop("error_message", "")
        user_type = request.session.get("user_type", "")
        
        context = { 
            "error_message" : error_message,
            "user_type" : user_type,
            "redirect_link" : request.GET.get("next", ""),
        }
        return render(request, self.template_name, context)

    # process form data
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user_type = request.POST.get("user_type")

        def _login():
            if user.is_active:
                # Remove alert
                request.session["alert"] = None
                login(request, user)

        referer = request.META.get("HTTP_REFERER")
        redirect_link = request.GET.get("next", "")
        # user = User.objects.filter(username=username).first()
        
        
        # returns User objects if credentials are correct
        user = authenticate(username=username, password=password)
        if not user:
            password  = password + settings.SECRET_KEY
            user = authenticate(username=username, password=password)

        # Student logins
        if user_type == "student":
            if user is not None:
                request.session["user_type"]  = user_type.lower()
                try:
                    if user.student:
                        _login()
                        if redirect_link:
                            return redirect(redirect_link)
                        return redirect("student:student")
                    request.session["error_message"] = "Please provide '{}' login details".format(user_type.upper())
                    return redirect(redirect_link)
                except Exception as e:
                    request.session["error_message"] = "Please provide '{}' login details".format(user_type.upper())
        
            request.session['error_message'] = 'Incorrect credentials'
            if redirect_link:    
                return redirect(redirect_link)
            return redirect(referer)
            
        if user:
            request.session["user_type"]  = user_type.lower()
            if user_type.lower() == "admin":                
                if user.is_superuser:
                    _login()
                    if redirect_link:
                        return redirect(redirect_link)
                    return redirect('dashboard:index')
                request.session["error_message"] = "Please provide '{}' login details".format(user_type.upper())
                return redirect(referer)

            elif user_type.lower() == "house master":
                try:
                    if user.staff.housemaster:
                       _login()
                       if redirect_link:
                            return redirect(redirect_link)
                       return redirect('staff:house_master') 
                except Exception as e:
                    print(e)
                    request.session["error_message"] = "Please provide '{}' login details".format(user_type.upper())
                    return redirect(referer)

            elif user_type.lower() == "form teacher":
                try:
                    if user.staff.student_class:
                        _login()
                        if redirect_link:
                            return redirect(redirect_link)
                        return redirect('staff:form_teacher')
                    request.session["error_message"] = "Please provide '{}' login details".format(user_type.upper())
                    return redirect(referer)
                except Exception as e:
                    request.session["error_message"] = "Please provide '{}' login details".format(user_type.upper())
                    return redirect(referer)

            elif user_type.lower() == "teacher":
                try:
                    _login()
                    if redirect_link:
                        return redirect(redirect_link)
                    if user.staff.teaches.all():
                        return redirect("staff:subject_teacher")
                    return redirect("staff:welcome")
                except Exception as e:
                    print(e)
                    request.session["error_message"] = "Please provide '{}' login details".format(user_type.upper())
                    return redirect(referer)
        context = {
            'error_message': 'Incorrect credentials',
        }
        return render(request, self.template_name, context)

def logout_user(request):
    logout(request)
    redirect_link = request.GET.get("next")
    
    if redirect_link:
        return redirect(redirect_link)
    
    return redirect('accounts:login')

# Admin logging into a staff account
def login_as(request, user_type, username):
    user = get_object_or_404(User, username=username)
    login(request, user)
    
    # Set alert
    request.session["alert"] = "Proxy Login!"

    request.session["user_type"]  = user_type.lower()
    if user_type.lower() == "house master":
        return redirect('staff:house_master')
    elif user_type.lower() == "form teacher":
        return redirect('staff:form_teacher')

    elif user_type.lower() == "teacher":
        return redirect("staff:subject_teacher")

    return redirect("staff:welcome")

def fetch_users(request):
    if not (request.user.is_authenticated and request.method == "POST"):
        return 
    query = request.POST.get("query")

    subject_teachers        = Staff.objects.filter(
                                Q(name__icontains=query) |
                                Q(staff_id__icontains=query)
                            )
    house_masters           = HouseMaster.objects.filter(
                                    Q(staff__name__icontains=query) |
                                    Q(staff__staff_id__icontains=query)
                                )
    classes            = StudentClass.objects.filter(
                                Q(class_teacher__name__icontains=query) |
                                Q(class_teacher__staff_id__icontains=query)
                                )

    context = {
        "subject_teachers":subject_teachers,
        "house_masters":house_masters,
        "classes":classes,
    }
    return render(request, "accounts/misc/search_template.html", context)
