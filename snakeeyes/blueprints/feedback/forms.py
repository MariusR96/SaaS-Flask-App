from flask_wtf import Form
from wtforms import TextAreaField
from wtforms_components import EmailField
from wtforms.validators import DataRequired, Length

class FeedbackForm(Form):
    email = EmailField('Email Adress',
                        [DataRequired(), Length(3,254)])

    feedback = TextAreaField('Please offer us your feedback.',
                                [DataRequired(), Length(1, 8192)])