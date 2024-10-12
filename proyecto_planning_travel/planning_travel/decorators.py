from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'logueo' not in request.session or 'rol' not in request.session['logueo'] or request.session['logueo']['rol'] != 1:
            return redirect('error') 
        return view_func(request, *args, **kwargs)
    return _wrapped_view