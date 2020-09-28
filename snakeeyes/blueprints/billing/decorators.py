from functools import wraps

import stripe
from flask import redirect, url_for, flash
from flask_login import current_user

def subscription_required(f):
    """
    Ensure a users has an active subscription. Otherwiese, 
    redirect to the pricing page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.subscription:
            return redirect(url_for('billing.pricing'))

        return f(*args, **kwargs)

    return decorated_function


def handle_stripe_exceptions(f):
    """
    A way to handle stripe exeptions so that we can deat with
    500 errors.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)

        except stripe.error.CardError:
            flash("Your card was declined. Please try again.", "error")
            return redirect(url_for('user.settings'))
        except stripe.error.InvalidRequestError as e:
            flash(e, 'error')
            return redirect(url_for('user.settings'))
        except stripe.error.AuthenticationError:
            flash("Authentication with our payment gateway failed", "error")
            return redirect(url_for('user.settings'))
        except stripe.error.APIConnectionError:
            flash("Our payment gateway is experiencing issues.", 'error')
            return redirect(url_for('user.settings'))
        except stripe.error.StripeError:
            flash('Our payment gateway is gaving issues, \
             please  try again.', 'error')
            return redirect(url_for('user.settings'))
    return decorated_function

