from flask import redirect, session
from functools import wraps

"""
Helpers.py uses parts of CS50: Finance

https://cs50.harvard.edu/college/2023/fall/psets/9/finance/ 
"""

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Decorate route to require login"""

        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function

def doctor_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Decorate route to require user type to be Doctor"""

        if session.get("user_type") is None or session.get("user_type") != "Doctor":
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function

def patient_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Decorate route to require user type to be Patient"""

        if session.get("user_type") is None or session.get("user_type") != "Patient":
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function
