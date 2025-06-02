from functools import wraps
from flask import session, url_for

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            print("Login necessário!")
            return url_for("auth.login")
        return func(*args, **kwargs)
    return wrapper