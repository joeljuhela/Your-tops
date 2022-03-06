from functools import wraps
from flask import redirect, url_for, request

from settings import ACCESS_TOKEN_COOKIE


def access_token_required(func):
    """
    Checks that the user has logged in with their access token
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        access_token = request.cookies.get(ACCESS_TOKEN_COOKIE)
        if access_token:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('auth_bp.login'))
    return wrapper
