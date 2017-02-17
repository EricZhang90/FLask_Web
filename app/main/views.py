from flask import render_template, abort
from . import main
from app.models import User


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('profile.html', user=user)

