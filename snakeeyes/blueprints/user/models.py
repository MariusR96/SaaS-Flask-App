import datetime
from collections import OrderedDict
from hashlib import md5

import pytz
from flask import current_app, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

from flask_login import UserMixin

from itsdangerous import URLSafeTimedSerializer, \
    TimedJSONWebSignatureSerializer

from lib.util_sqlalchemy import ResourceMixin, AwareDateTime
from snakeeyes.blueprints.billing.models.credit_card import CreditCard
from snakeeyes.blueprints.billing.models.subscription import Subscription
from snakeeyes.blueprints.billing.models.invoice import Invoice
from snakeeyes.blueprints.bet.models.bet import Bet
from snakeeyes.extensions import db



class User(UserMixin, ResourceMixin, db.Model):
    ROLE = OrderedDict([
        ('member', 'Member'),
        ('admin', 'Admin')
    ])

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    #Relationships
    credit_card = db.relationship(CreditCard, uselist=False, backref='users',
                                  passive_deletes=True)
    subscription = db.relationship(Subscription, uselist=False, backref='users',
                                  passive_deletes=True)
    invoices = db.relationship(Invoice, backref='users', passive_deletes=True)
    bets = db.relationship(Bet, backref='users', passive_deletes=True)
    #Authentication
    role = db.Column(db.Enum(*ROLE, name='role_types', native_enum=False),
                    index=True, nullable=False, server_default='member')

    active = db.Column('is_active', db.Boolean(), nullable=False,
                        server_default='1')
    username = db.Column(db.String(24), unique=True, index=True)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False,
                        server_default='')
    password = db.Column(db.String(128), nullable=False, server_default='')

    verified = db.Column('is_verified', db.Boolean(), nullable=False,
                          default=False)
    #Billing
    name = db.Column(db.String(128), index=True)
    payment_id = db.Column(db.String(128), index=True)
    cancelled_subscription_on = db.Column(AwareDateTime())
    previous_plan = db.Column(db.String(128))

    # Bet
    coins = db.Column(db.BigInteger())
    last_bet_on = db.Column(AwareDateTime())

    #Activity tracking.
    sign_in_count = db.Column(db.Integer, nullable=False, default=0)
    current_sign_in_on = db.Column(AwareDateTime())
    current_sign_in_ip = db.Column(db.String(45))
    last_sign_in_on = db.Column(AwareDateTime())
    last_sign_in_ip = db.Column(db.String(45))


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        self.password = User.encrypt_password(kwargs.get('password', ''))
        
    @classmethod
    def find_by_identity(cls, identity):
        """
        Find a user by usernam or email
        
        :param identity: username or email
        :return: User instance
        """
        current_app.logger.debug(f'{identity} has tried to login.')

        return User.query.filter(
            (User.email == identity) | (User.username == identity)).first()
        
    @classmethod
    def encrypt_password(cls, plaintext_password):
        """
        Hashing a plaintext string using PBKDF2
        :param plaintext_passwod: Password in plain text.
        :return: str
        """
        if plaintext_password:
            return generate_password_hash(plaintext_password)

        return None

    @classmethod
    def deserialize_token(cls, token):
        """
        Obtain a uesr from deserializing a signed token
        
        :param token: Signed token
        :return: User instance or None
        """
        private_key = TimedJSONWebSignatureSerializer(
            current_app.config['SECRET_KEY']
        )
        try:
            decoded_payload = private_key.loads(token)

            return User.find_by_identity(decoded_payload.get('user_email'))
        except Exception:
            return None

    @classmethod
    def initialize_password_reset(cls, identity):
        """
        Generate a token to reset the password for a specific user.

        :param identity: User e-mail address or username
        :type identity: str
        :return: User instance
        """
        u = User.find_by_identity(identity)
        reset_token = u.serialize_token()

        # This prevents circular imports.
        from snakeeyes.blueprints.user.tasks import (
            deliver_password_reset_email)
        deliver_password_reset_email.delay(u.id, reset_token)

        return u
    
    @classmethod
    def validate_account(cls, identity):
        u = User.find_by_identity(identity)
        validation_token = u.serialize_token()
        print("$$$$$$$$$$$$$$$$", validation_token)

        from snakeeyes.blueprints.user.tasks import (
            deliver_confirmation_mail)

        deliver_confirmation_mail(u.id, validation_token)
        
        return u 


    def is_active(self):
        """
        Return whether or not the user account is active, this satisfies
        Flask-Login by overwriting the default value.

        :return: bool
        """
        return self.active

    def is_verified(self):
        """
        See if the user is verified.

        :return: bool
        """
        return self.verified


    def get_auth_token(self):
        """
        Return the user's auth token. Use their password as part of the token
        because if the user changes their password we will want to invalidate
        all of their logins across devices. It is completely fine to use
        md5 here as nothing leaks.

        This satisfies Flask-Login by providing a means to create a token.

        :return: str
        """

        private_key = current_app.config['SECRET_KEY']
        serializer = URLSafeTimedSerializer(private_key)
        data = [str(self.id), md5(self.password.encode('utf-8')).hexdigest()]

        return serializer.dumps(data)

    
    def authenticated(self, with_password=True, password=''):
        """
        Ensure a user is authenticated, and optionally check their password.

        :param with_password: Optionally check their password
        :type with_password: bool
        :param password: Optionally verify this as their password
        :type password: str
        :return: bool
        """
        if with_password:
            return check_password_hash(self.password, password)

        return True

    
    def serialize_token(self, expiration=3600):
        """
        Sign and create a token that can be used for things such as resetting
        a password or other tasks that involve a one off token.

        :param expiration: Seconds until it expires, defaults to 1 hour
        :type expiration: int
        :return: JSON
        """
        private_key = current_app.config['SECRET_KEY']

        serializer = TimedJSONWebSignatureSerializer(private_key, expiration)
        
        return serializer.dumps({'user_email': self.email}).decode('utf-8')

    def update_activity_tracker(self, ip_address):
        """
        Update various fields on the user that's related to meta data on their
        account, such as the sign in count and ip address, etc..

        :param ip_address: IP address
        :type ip_address: str
        :return: SQLAlchemy commit results
        """ 
        self.sign_in_count +=1
        self.last_sign_in_on = self.current_sign_in_on
        self.last_sign_in_ip = self.current_sign_in_ip

        self.current_sign_in_on = datetime.datetime.now(pytz.utc)
        self.current_sign_in_ip = ip_address

        return self.save()


    @classmethod
    def search(cls, query):
        """
        Search a result by 1 or more fields.

        :param query: search query
        :return: SQLAlchemy filter
        """
        print("#######################", str(query))
        if query == '':
            return ''

        search_query = '%{0}%'.format(query)
        search_chain = (User.email.ilike(search_query),
                        User.username.ilike(search_query))

        return or_(*search_chain)

    
    @classmethod
    def is_last_admin(cls, user, new_role, new_active):
        """
        Check  if the user is the last admin account.

        :param user: User being tested
        :param new_role: New role being set
        :param new_active: New active status being set
        :return: bool
        """
        is_changing_roles = user.role == 'admin' and new_role != 'admin'
        is_changing_active = user.active is True and new_active is None

        if is_changing_roles or is_changing_active:
            admin_count = User.query.filter(User.role == 'admin').count()
            active_count = User.query.filter(User.is_active is True).count()

            if admin_count == 1 or active_count == 1:
                return True

        return False


    def add_coins(self, plan):
        """
        Add an amount of coins to an existing user.

        :param plan: Subscription plan
        :return: SQLAlchemy commit results
        """
        self.coins += plan['metadata']['coins']

        return self.save()

