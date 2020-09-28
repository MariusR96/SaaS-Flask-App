from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user

def coins_required(f):
    """
    Restrict acces for users who have no coins.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.coins == 0:
            flash("You're out of coins!", "warning")
            return redirect(url_for('user.settings'))

        return f(*args, **kwargs)

    return decorated_function