from sqlalchemy import func

from snakeeyes.blueprints.user.models import db, User
from snakeeyes.blueprints.billing.models.subscription import Subscription
from snakeeyes.blueprints.bet.models.bet import Bet

class Dashboard(object):
    @classmethod
    def group_and_count_users(cls):
        """
        Perform a group by/count on all users.
        :return: dictionary
        """

        return Dashboard._group_and_count(User, User.role)

    @classmethod
    def group_and_count_plans(cls):
        """
        Perform a group by/count on all subscriber types.

        :return: dict
        """
        return Dashboard._group_and_count(Subscription, Subscription.plan)

    
    @classmethod
    def group_and_count_coupons(cls):
        """
        Obtain coupon usage statistics across all subscribers.

        :return: tuple
        """
        not_null = db.session.query(Subscription).filter(
            Subscription.coupon.isnot(None)).count()
        total = db.session.query(func.count(Subscription.id)).scalar()

        if total == 0:
            percent = 0
        else:
            percent = round((not_null / float(total)) * 100, 1)
        return not_null, total, percent

    @classmethod
    def group_and_count_payouts(cls):
        """
        Perform a group by/count on all payouts.

        :return: dict
        """

        count = func.count(Bet.payout).filter(Bet.net > 0)
        query = db.session.query(count, Bet.payout) \
            .filter(Bet.net > 0).group_by(Bet.payout).all()

        results = {
            'query': query,
            'total': Bet.query.filter(Bet.net > 0).count()
        }  
        return results

        #return Dashboard._group_and_count(Bet, Bet.payout)

    @classmethod
    def _group_and_count(cls, model, field):
        """
        Group results for a specific model and field.

        :param model: Name of the model
        :type model: SQLAlchemy model
        :param field: Name of the field to group on
        :type field: SQLAlchemy field
        :return: dict
        """
        count = func.count(field) 
        query = db.session.query(count, field).group_by(field).all()

        results = {
            'query': query,
            'total': model.query.count()
        }  

        return results
