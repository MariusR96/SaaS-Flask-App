def cents_to_dollars(cents):
    """
    Convert cents to dollars
    """
    return round(cents/100.0, 2)

def dollars_to_cents(dollars):
    """
    Convert dollars to cents.
    """
    return int(dollars * 100)
    