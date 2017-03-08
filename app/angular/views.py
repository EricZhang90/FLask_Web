from flask import render_template
from . import angular

@angular.route('/')
def index():
    return render_template('angular/index.html')