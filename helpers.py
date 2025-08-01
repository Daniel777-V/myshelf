from functools import wraps
from flask import redirect, session, flash


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Login required for this action")
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
