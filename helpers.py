from flask import redirect, render_template, session
from functools import wraps

def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_type")!= "Doctor":
            session.clear()
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function

def patient_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_type")!= "Patient":
            session.clear()
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function
