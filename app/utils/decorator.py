from functools import wraps
from flask import session, redirect, url_for, request


def custom_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            print(request.url)
            return redirect(url_for('user.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
