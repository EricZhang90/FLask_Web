from . import api
from flask import jsonify, g, request, url_for, current_app
from ..models import User, Follow



@api.route('/user/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({'user': user.to_json()})

@api.route('/followed/<int:id>')
def followed(id):
    user = User.query.get_or_404(id)
    page_num = request.args.get('page', 1, type=int)
    pagination = user.followed.order_by(Follow.timestamp) \
                              .paginate(page_num,
                                        per_page=current_app.config['PW_POSTS_PER_PAGE'],
                                        error_out=False)
    return jsonify(
        [{'username': item.followed.username,
          'url': url_for('api.get_user', id=item.followed.id, _external=True),
          'timestamp': item.timestamp
          } for item in pagination.items if item.followed.id != user.id]
    )


@api.route('/followers/<int:id>')
def followers(id):
    user = User.query.get_or_404(id)
    page_num = request.args.get('page', 1, type=int)
    pagination = user.followers.order_by(Follow.timestamp) \
                              .paginate(page_num,
                                        per_page=current_app.config['PW_POSTS_PER_PAGE'],
                                        error_out=False)
    return jsonify(
        [{'username': item.follower.username,
          'url': url_for('api.get_user', id=item.follower.id, _external=True),
          'timestamp': item.timestamp
          } for item in pagination.items if item.follower.id != user.id]
    )