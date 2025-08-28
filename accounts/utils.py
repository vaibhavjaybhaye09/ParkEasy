from functools import wraps
from django.shortcuts import render, redirect


def role_required(allowed_roles):
    if isinstance(allowed_roles, str):
        allowed = {allowed_roles}
    else:
        allowed = set(allowed_roles)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            try:
                role = request.user.role
            except Exception:
                return redirect('login')
            if role not in allowed:
                return render(request, 'accounts/forbidden.html', status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
