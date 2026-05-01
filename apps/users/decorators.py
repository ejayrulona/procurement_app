from django.shortcuts import redirect
from functools import wraps

def admin_required(view_function):
    @wraps(view_function)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            return redirect("core:home")
        
        return view_function(request, *args, **kwargs)
    
    return wrapper

def any_admin_required(view_function):
    @wraps(view_function)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_any_admin:
            return redirect("core:home")
        
        return view_function(request, *args, **kwargs)
    
    return wrapper

def college_required(view_function):
    @wraps(view_function)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_college:
            return redirect("core:home")
        
        return view_function(request, *args, **kwargs)
    
    return wrapper