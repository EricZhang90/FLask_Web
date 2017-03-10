from flask import render_template
from . import angular
from ..models import User, Post
import time

@angular.route('/')
def index():
    admin = User.query.filter_by(username='Main_Tester').first()
    posts = [{
              'body': posts.body,
              'timestamp': str(time.mktime(posts.timestamp.timetuple()))
             }
                for posts in admin.posts.order_by(Post.timestamp.desc()).all()]

    return render_template('angular/index.html', posts=posts)