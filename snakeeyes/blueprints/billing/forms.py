from flask_wtf import Form
from wtforms import StringField, HiddenField, SelectField
from wtforms.validators import DataRequired, Optional, Length

from config.settings import COIN_BUNDLES

class SubscriptionForm(Form):
    stripe_key = HiddenField('Stripe publishable key',
                            [DataRequired(), Length(1, 254)])

    plan = HiddenField('Plan', [DataRequired(), Length(1, 254)])
    coupon_code = StringField('Do you have a coupon code?', 
                                [Optional(), Length(1,128)])
    name = StringField('Name on card', [DataRequired(), Length(1, 254)])


class UpdateSubscriptionForm(Form):
    coupon_code = StringField('Do you have a coupon code?', 
                            [Optional(), Length(1, 254)])


class CancelSubscriptionForm(Form):
    pass

def choices_from_bundles():

    choices = []

    for bundle in COIN_BUNDLES:
        pair = (str(bundle.get('coins')), bundle.get('label'))
        choices.append(pair)

    return choices

class PaymentForm(Form):
    stripe_key = HiddenField('Stripe publishable key',
                            [DataRequired(), Length(1, 254)])

    coin_bundles = SelectField('How many coins do you want to purchase?',
                                [DataRequired()], choices=choices_from_bundles())
    
    coupon_code = StringField('Do you have a coupon code?',
                              [Optional(), Length(1, 128)])
    name = StringField('Name on card',
                       [DataRequired(), Length(1, 254)])