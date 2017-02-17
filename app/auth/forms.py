from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from ..models import User



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(3,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(3,64), Email()])

    username = StringField('Username', validators=[Required(),
                                                   Length(1, 64),
                                                   Regexp('^[A-Za-z][A-Za-z0-9_,]*$', 0,
                                                          'Username must have only letters,'
                                                          'numbers, dots or underscores')])
    password = PasswordField('Password', validators=[Required(),
                                                     EqualTo('password2', message='Passwords must match'),
                                                     Length(8, 128, 'Length of password must be 8 - 128')])
    password2 = PasswordField('Confirm Password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already registered.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Current Password', validators=[Required(),
                                                     Length(8, 128, 'Length of password must be 8 - 128')])
    new_password = PasswordField('New Password', validators=[Required(),
                                                     EqualTo('new_password2', message='Passwords must match'),
                                                     Length(8, 128, 'Length of password must be 8 - 128')])
    new_password2 = PasswordField('Confirm Password', validators=[Required()])
    submit = SubmitField('Change Password')

    def cleanForm(self):
        self.old_password.data = ""
        self.new_password.data = ""
        self.new_password2.data = ""


class ChangeEmailForm(FlaskForm):
    password = PasswordField('Current Password', validators=[Required()])
    email = StringField('New Email', validators=[Required(), Length(3,64), Email()])
    submit = SubmitField('Change Email')

    def cleanForm(self):
        self.email.data = ""


class RestPasswordForm(FlaskForm):
    email = StringField('Registered Email', validators=[Required(), Length(3,64), Email()])
    password = PasswordField('Password', validators=[Required(),
                                                     EqualTo('password2', message='Passwords must match'),
                                                     Length(8, 128, 'Length of password must be 8 - 128')])
    password2 = PasswordField('Confirm Password', validators=[Required()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')
