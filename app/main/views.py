from flask import render_template, abort, flash, redirect, url_for, request, current_app, make_response
from . import main
from .. import db
from app.models import User, Role, Permission, Post, Comment
from app.decorators import amdin_required, permission_required
from forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from flask_login import login_required, current_user



@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    page_num = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(page=page_num,
                                            per_page=current_app.config['PW_POSTS_PER_PAGE'],
                                            error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination, show_followed=show_followed)


@main.route('/show_all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/show_followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    page_num = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page=page_num,
                                            per_page=current_app.config['PW_POSTS_PER_PAGE'],
                                            error_out=False)
    posts = pagination.items
    return render_template('profile.html', user=user, posts=posts, pagination=pagination)


@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.profile', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit_profile/<int:id>', methods=['POST', 'GET'])
@login_required
@amdin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.role = Role.query.get(form.role.data)
        user.email = form.email.data
        user.confirmed = form.confirmed.data
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('main.profile', username=user.username))
    form.username.data = user.username
    form.role = user.role_id
    form.email.data = user.email
    form.confirmed.data = user.confirmed
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=post, author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('Comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page_num = request.args.get('page', 1, type=int)
    if page_num == -1:
        page_num = (post.comments.count() - 1) / current_app.config['PW_POSTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page_num,
                                        per_page=current_app.config['PW_POSTS_PER_PAGE'],
                                        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post],
                           form=form, comments=comments,
                           pagination=pagination)


@main.route('/eidt_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and current_user.can(Permission.ADMINISTER) == False:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/delete_post/<int:id>')
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and current_user.can(Permission.ADMINISTER) == False:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('The post has been deleted.')
    return redirect(url_for('.index'))


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.profile', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user) == False:
        flash("You haven't followed this user.")
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s now.' % username)
    return redirect(url_for('.profile', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page_num = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page_num,
                                    per_page=current_app.config['PW_POSTS_PER_PAGE'],
                                    error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items if item.follower.id != user.id]
    return render_template('followers.html',
                           user=user,
                           title='Followers of',
                           endpoint='.followers',
                           pagination=pagination,
                           follows=follows)


@main.route('/followed/<username>')
def followed(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page_num = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page_num,
                                    per_page=current_app.config['PW_POSTS_PER_PAGE'],
                                    error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items if item.followed.id != user.id]
    return render_template('followers.html',
                           user=user,
                           title='Followed of',
                           endpoint='.followers',
                           pagination=pagination,
                           follows=follows)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    post = Post.query.filter(Post.comments.any(id=id)).first()
    comment.disable = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.post', id=post.id, page=request.args.get('page', 1, type=int), _anchor=id))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    post = Post.query.filter(Post.comments.any(id=id)).first()
    comment.disable = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.post', id=post.id, page=request.args.get('page', 1, type=int), _anchor=id))








