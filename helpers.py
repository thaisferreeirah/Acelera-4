from functools import wraps
from flask import session, url_for, redirect
from pyttslib import TextToSpeech

tts = TextToSpeech(engine="google", engine_config={"lang": "pt-br"})

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            print("Login necessário!")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wrapper

def announce_authorized(name):
    tts.speak(f"Seja bem vindo, {name}!")