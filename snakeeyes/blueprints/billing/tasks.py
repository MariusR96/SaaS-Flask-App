from snakeeyes.app import create_celery_app
from snakeeyes.blueprints.user.models import User
from snakeeyes.blueprints.billing.models.credit_card import CreditCard
from snakeeyes.blueprints.billing.models.coupon import Coupon

celery = create_celery_app()


@celery.task()
def mark_old_credit_cards():
    """
    Mark credit cards that are expired or are going to expire soon.
    :return: Result of updating records
    """
    return CreditCard.mark_old_credit_cards()


@celery.task()
def expire_old_coupons():
    """
    Invalidate coupons that are expired.
    :return: Update records
    """
    return Coupon.expire_old_coupons()


@celery.task()
def delete_users(ids):
    """
    Delete users and cancel their subscriptions.

    :param ids: List of ids to be canceled.
    :return: Bulk delete users.
    """
    return User.bulk_delete(ids)


@celery.task()
def delete_coupons(ids):
    """
    Delete coupons on the payment gateway and locally.

    :param ids: List of ids to be deleted.
    :return: Bulk delete coupons.
    """

    return Coupon.bulk_delete(ids)


