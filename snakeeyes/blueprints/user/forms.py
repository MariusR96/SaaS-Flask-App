from flask_wtf import Form
from wtforms import HiddenField, StringField, PasswordField
from wtforms.validators import DataRequired, Length, Optional, Regexp
from wtforms_components import EmailField, Email, Unique

from lib.util_wtforms import ModelForm, choices_from_dict
from snakeeyes.blueprints.user.models import User, db
from snakeeyes.blueprints.user.validations import ensure_identity_exists, \
    ensure_existing_password_matches


class LoginForm(Form):
    next = HiddenField()
    identity = StringField('Username or email',
                            [DataRequired(), Length(3,254)])
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])


class BeginPasswordResetForm(Form):
    identity = StringField('Username or email',
                            [DataRequired(),
                            Length(3,254),
                            ensure_identity_exists])


class PasswordResetForm(Form):
    reset_token = HiddenField()
    password = PasswordField('Password', [DataRequired(), Length(8,128)])


class AccountValidationForm(Form):
    validation_token = HiddenField()

class SignupForm(ModelForm):
    email = EmailField(validators=[
        DataRequired(),
        Email(),
        Unique(
            User.email,
            get_session=lambda: db.session
        )
    ])
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])


class WelcomeForm(ModelForm):
    username_message = 'Letters, numbers, and underscores only'

    username = StringField(validators=[
        Unique(
            User.username,
            get_session=lambda: db.session
        ),
        DataRequired(),
        Length(1, 16),
        Regexp('^\w+$', message=username_message)
    ])


class UpdateCredentials(ModelForm):
    current_password = PasswordField('Current password',
                                [DataRequired(),
                                Length(8, 128),
                                ensure_existing_password_matches])

    email = EmailField(validators=[
        Email(),
        Unique(
            User.email,
            get_session=lambda: db.session
        )
    ])
    password = PasswordField('Password', [Optional(), Length(8, 128)])
