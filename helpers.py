from flask import redirect, render_template, session
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function

def doctor_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_type") is None or session.get("user_type") != "Doctor":
            return redirect("/") #change later to an error page of access denied
        return f(*args, **kwargs)

    return decorated_function

def patient_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_type") is None or session.get("user_type") != "Patient":
            return redirect("/") #change later to error page of access denied
        return f(*args, **kwargs)

    return decorated_function
