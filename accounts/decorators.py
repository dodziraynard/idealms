import functools
from django.shortcuts import redirect

def logged_in_as(user_type):
    def logged_in_as_decorator(func):
        @functools.wraps(func)
        def wrapper_check_user(*args, **kwargs):
            request = args[0]
            if not request.user.is_authenticated:
                return redirect("accounts:login")
            if not request.user_type == user_type:
                request.session["user_not_permitted_error"] = "Access denied!"
                return redirect("accounts:login")
            return func(*args, **kwargs)
        return wrapper_check_user
    return logged_in_as_decorator

def login_required(func):
    @functools.wraps(func)
    def wrapper_logged_in(*args, **kwargs):
        request = args[0]
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        return func(*args, **kwargs)
    return wrapper_logged_in