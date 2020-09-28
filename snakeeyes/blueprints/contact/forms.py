from flask_wtf import Form
from wtforms import TextAreaField
from wtforms_components import EmailField
from wtforms.validators import DataRequired, Length

class ContactForm(Form):
    email = EmailField("Email Adress",
                        validators=[DataRequired(), Length(3, 254)])
                    
    message = TextAreaField("What is your issue?",
                        [DataRequired(), Length(1, 8192)])


class MailForm(Form):
    pass