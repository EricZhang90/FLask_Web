from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, ChangeEmailForm
from ..email import send_email

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()

        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    elif current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')

    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    passwordForm = ChangePasswordForm()
    if passwordForm.validate_on_submit():
        if current_user.verify_password(passwordForm.old_password.data):
            current_user.password = passwordForm.new_password.data
            flash('Password has been changed')
        else:
            flash('Password is incorrect.')
        passwordForm.cleanForm()
        return redirect(url_for('auth.change_password'))
    return render_template('auth/change_password.html', passwordForm=passwordForm)

@auth.route('/request_change_email', methods=['GET', 'POST'])
@login_required
def request_change_email():
    emailForm = ChangeEmailForm()
    if emailForm.validate_on_submit():
        if current_user.verify_password(emailForm.password.data):
            token = current_user.generate_change_email_token(new_email=emailForm.email.data)
            send_email(emailForm.email.data, 'Confirm Email Change', 'auth/email/change_email', user=current_user, token=token)
            flash('A new confirmation email has been sent to you by new email address. Please confirm it in order to change your email.')
            return redirect(url_for('main.index'))
        else:
            flash('Password is incorrect. Please enter correct password.')

    return render_template('auth/change_email.html', emailForm=emailForm)

@auth.route('/change_email/<token>')
def change_email(token):
    try:
        current_user.change_email_by_token(token)
    except:
        flash('Token is invalid, please send a new token')
        return render_template('auth/change_email.html', emailForm=ChangeEmailForm())
    flash('Email has been changed.')
    return redirect(url_for('main.index'))

@auth.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

















