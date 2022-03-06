import os
from app.auth import auth_bp
from flask import Flask, redirect, request, render_template, url_for

from settings import ACCESS_TOKEN_COOKIE
from api import SpotifyAPI
from app.utils import access_token_required
from app.forms import SpotifyTimeSearchForm


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(auth_bp, url_prefix='/auth')

    @app.template_filter('humanize_ms')
    def humanize_ms(ms):
        """Turn time given in milliseconds to a human-readable string format (mm:ss)"""
        seconds = ms / 1000
        minutes = int(seconds / 60)
        return f"{minutes}:{int(seconds % 60):0>2d}"

    @app.route('/', methods=['GET', 'POST'])
    @access_token_required
    def main():
        access_token = request.cookies.get(ACCESS_TOKEN_COOKIE)
        api = SpotifyAPI(access_token)
        user = api.get_user()
        display_name = user['display_name']
        form = SpotifyTimeSearchForm(request.form)
        if request.method == 'POST' and form.validate():
            top_type = form.top_type.data
            time_range = form.time_range.data
            top_items = api.get_user_top_items(top_type, time_range)
            print(top_type, time_range)
            return render_template('main.html', user=display_name, top_type=top_type, top_items=top_items, form=form)
        return render_template('main.html', user=display_name, form=form)

    return app
