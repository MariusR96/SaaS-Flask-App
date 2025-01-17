import datetime
import pytz

from lib.money import cents_to_dollars

def format_currency(amount, convert_to_dollars=True):
    """
    Pad currency with 2 decimals and commas,
    optionally covert cents to dollars.
    :param amount: Amount in cents or dollars
    :type amount: int or float
    :param convert_to_dollars: Convert cents to dollars
    :type convert_to_dollars: bool
    :return: str
    """
    if convert_to_dollars:
        amount = cents_to_dollars(amount)

    return '{:,.2f}'.format(amount)


def current_year():
    """
    Return this year
    :return int
    """
    return datetime.datetime.now(pytz.utc).year