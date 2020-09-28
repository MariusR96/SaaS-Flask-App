from flask import jsonify

def render_json(status, *args, **kwargs):
    """
    Return a JSON response.

    Example:
        render_json(404, {'error': 'Discount code not found.'})

    :param status: HTTP status code
    :type status: int
    :param args:
    :param kwargs:
    :return: Flask response
    """
    response = jsonify(*args, **kwargs)
    response.status_code = status

    return response
        