from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user

def anonymous_required(url='/settings'):
    """
    Redirect a user to a specified location if they are already signed in.

    :param url: URL to be redirected to if invalid
    :type url: str
    :return: Function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                return redirect(url)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def role_required(*roles):
    """
    Does a user have permission to view this page?

    :param *roles: 1 or more allowed roles
    :return: Function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                flash('You do not have permission to do that.', 'error')
                return redirect('/')

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def activation_required(f):
    """
    Only activated accounts cand perform these actions.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_verified():
            flash("You need to activate your account!")
            return redirect(url_for('user.settings'))
        return f(*args, **kwargs)
    return decorated_function

