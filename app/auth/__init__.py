from flask import Blueprint

auth = Blueprint('name', __name__)

from . import views
