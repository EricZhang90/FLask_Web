from . import api
from flask import jsonify, g, request, url_for, current_app
from ..models import Comment



@api.route('/comment/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify({'comment': comment.to_json()})

@api.route('/post/<int:id>/comments')
def get_post_comments(id):
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.filter_by(post_id=id) \
                              .order_by(Comment.timestamp.desc()) \
                              .paginate(page,
                                        per_page=current_app.config['PW_POSTS_PER_PAGE'],
                                        error_out=False)
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.post_comments', page=page-1, id=id, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.post_comments', page=page+1, id=id, _external=True)
    return jsonify({
        'prev': prev,
        'next': next,
        'count': pagination.total,
        'posts': [comment.to_json() for comment in comments]
    })