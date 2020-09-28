from lib.flask_mailplus import send_template_message
from snakeeyes.app import create_celery_app

celery = create_celery_app()

@celery.task()
def deliver_feedback_email(email, feedback):

    ctx = {'email': email, 'feedback': feedback}

    send_template_message(subject='[Snake Eyes] Feedback',
                        sender=email,
                        recipients=[celery.conf.get('MAIL_USERNAME')],
                        reply_to=email,
                        template='feedback/mail/index', ctx=ctx)