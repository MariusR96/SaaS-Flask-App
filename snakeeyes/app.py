import logging

from logging.handlers import SMTPHandler
from flask_login import current_user
import stripe

from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, render_template
from celery import Celery
from itsdangerous import URLSafeTimedSerializer

from snakeeyes.blueprints.admin import admin
from snakeeyes.blueprints.page import page
from snakeeyes.blueprints.contact import contact
from snakeeyes.blueprints.feedback import feedback
from snakeeyes.blueprints.user import user
from snakeeyes.blueprints.bet import bet
from snakeeyes.blueprints.user.models import User
from snakeeyes.blueprints.billing import billing
from snakeeyes.blueprints.billing import stripe_webhook
from snakeeyes.blueprints.billing.template_processors import(
    format_currency,
    current_year
)
from snakeeyes.extensions import (
    debug_toolbar,
    mail,
    csrf,
    db,
    login_manager,
    limiter
    )
from werkzeug.utils import cached_property

CELERY_TASK_LIST = [
    'snakeeyes.blueprints.contact.tasks',
    'snakeeyes.blueprints.feedback.tasks',
    'snakeeyes.blueprints.user.tasks',
    'snakeeyes.blueprints.billing.tasks'
]


def create_celery_app(app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'],
                    include=CELERY_TASK_LIST)
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=True)

    if settings_override:
        app.config.update(settings_override)

    app.logger.setLevel(app.config['LOG_LEVEL'])

    stripe.api_key = app.config.get('STRIPE_SECRET_KEY')
    stripe.api_version = app.config.get('STRIPE_API_VERSION')

    middleware(app)
    error_templates(app)
    exception_handler(app)
    app.register_blueprint(admin)
    app.register_blueprint(page)
    app.register_blueprint(contact)
    app.register_blueprint(billing)
    app.register_blueprint(stripe_webhook)
    app.register_blueprint(feedback)
    app.register_blueprint(user)
    app.register_blueprint(bet)
    template_processors(app)
    extensions(app)
    authentication(app, User)


    return app

def extensions(app):
    """
    Register extensions.

    :param app: Flask application instance
    :return: None
    """

    debug_toolbar.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    return None

def template_processors(app):
    """
    Register 0 or more custom template processors (mutates the app passed in).

    :param app: Flask application instance
    :return: App jinja environment
    """
    app.jinja_env.filters['format_currency'] = format_currency
    app.jinja_env.globals.update(current_year=current_year)

    return app.jinja_env

def authentication(app, user_model):
    """
    Initialization of the Flask-Login extension

    :param app: Flask application instance
    :param user_model: Model that contains the information for authentication
    :type user_model: SQLAlchemy model
    :return: None
    """
    login_manager.login_view = 'user.login'

    @login_manager.user_loader
    def load_user(uid):
        return user_model.query.get(uid)


    @login_manager.token_loader
    def load_token(token):
        duration = app.config['REMEMBER_COOKIE_DURATION'].total_seconds()
        serializer = URLSafeTimedSerializer(app.secret_key)

        data = serializer.loads(token, max_age=duration)
        user_uid = data[0]

        return user_model.query.get(user_uid)



def middleware(app):
    """
    Register middleware.
    :param app: Flask instance
    :return: None
    """

    app.wsgi_app = ProxyFix(app.wsgi_app)

    return None


def error_templates(app):
    """
    Register costum error pages.
    :param app: Flask app instance
    :return: None
    """

    def render_status(status):
        """
        Render custom template for a specific status.

        :param status: Status as a written name
        :return: None
        """

        status_code = getattr(status, 'code', 500)
        return render_template(f'errors/{status_code}.html'), status_code

    for error in [404, 429, 500]:
        app.errorhandler(error)(render_status)

    return None


def exception_handler(app):
    """
    Register exeption handlers
    :param app: Flask app instance
    :return: None
    """
    mail_handler = SMTPHandler((app.config.get('MAIL_SERVER'),
                                app.config.get('MAIL_PORT')),
                                app.config.get('MAIL_USERNAME'),
                                [app.config.get('MAIL_USERNAME')],
                                '[EXCEPTIION handler] A 5xx was thrown',
                                (app.config.get('MAIL_USERNAME'),
                                app.config.get('MAIL_PASSWORD')),
                                secure=())

    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter("""
    Time:               %(asctime)s
    Message type:       %(levelname)s


    Message:

    %(message)s
    """))
    app.logger.addHandler(mail_handler)

    return None