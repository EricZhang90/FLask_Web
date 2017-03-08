from flask import Blueprint

angular = Blueprint('angular', __name__)

from . import views