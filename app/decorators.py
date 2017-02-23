from flask import abort
from functools import wraps
from flask_login import current_user
from .models import Permission

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.can(permission) == False:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def amdin_required(f):
    return permission_required(Permission.ADMINISTER)(f)
