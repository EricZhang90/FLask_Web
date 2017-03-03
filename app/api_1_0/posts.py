from . import api
from .authentication import auth
from flask import jsonify, g, request, url_for
from ..models import Post, Permission
from .decorators import permission_required
from .. import db
from errors import forbidden



@api.route('/posts/')
@auth.login_required
def get_posts():
    posts = Post.query.all()
    return jsonify({'posts': [post.to_json() for post in posts]})


@api.route('/post/<int:id>')
@auth.login_required
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify({'post': post.to_json()})


@permission_required(Permission.WRITE_ARTICLES)
@api.route('/posts/', methods=['POST'])
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
                {'Location': url_for('api.get_post', id=post.id, _external=True)}


@permission_required(Permission.WRITE_ARTICLES)
@api.route('/post/<int:id>', methods=['PUT'])
def edit_post(id):
    post = Post.query.get_or_404(id)
    if post.author != g.current_user and not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())
















