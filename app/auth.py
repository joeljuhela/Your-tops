import secrets
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urlencode

from flask import Blueprint, make_response, redirect, request, render_template, url_for

from config import CLIENT_ID, REDIRECT_URI, CLIENT_SECRET, ACCESS_TOKEN_COOKIE


auth_bp = Blueprint('auth_bp', __name__,
                    template_folder='templates',
                    static_folder='static', static_url_path='static')

cookie_key = 'your_tops_auth_state'


@auth_bp.route('/login')
def login():
    return render_template('auth/login.html')


@auth_bp.route('/login-spotify')
def spotify_login():
    state = secrets.token_urlsafe(8)

    query_str = urlencode({
        "response_type": "code",
        "client_id": CLIENT_ID,
        "scope": "playlist-modify-private playlist-modify-public user-top-read ugc-image-upload",
        "redirect_uri": REDIRECT_URI,
        "state": state
    })

    res = make_response(redirect('https://accounts.spotify.com/authorize?' + query_str))
    res.set_cookie(cookie_key, state)
    return res


@auth_bp.route('/logout')
def logout():
    res = make_response(redirect(url_for('main')))
    res.delete_cookie(ACCESS_TOKEN_COOKIE)
    return res


@auth_bp.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    stored_state = request.cookies.get(cookie_key)
    if not state or state != stored_state:
        return redirect('/error')
    else:

        auth = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
        }
        r = requests.post(
            'https://accounts.spotify.com/api/token',
            auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
            data=auth
        )

        if r.status_code == 200:
            body = r.json()
            access_token = body['access_token']
            res = make_response(redirect(url_for('main')))
            # Spotify Access Tokens last for a short while (approx. 1h)
            res.set_cookie(ACCESS_TOKEN_COOKIE, access_token, max_age=60*60)
        else:
            res = make_response(redirect('/error'))

        res.delete_cookie(cookie_key)
        return res
