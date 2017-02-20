from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms.validators import Length, ValidationError, Required, Regexp, Email
from ..models import Role, User

class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Update')


class EditProfileAdminForm(FlaskForm):
    username = StringField('Username', validators=[Required(),
                                                   Length(1, 64),
                                                   Regexp('^[A-Za-z][A-Za-z0-9_,]*$', 0,
                                                          'Username must have only letters,'
                                                          'numbers, dots or underscores')])
    role =  SelectField('Role', coerce=int)
    email = StringField('Email', validators=[Required(), Length(3,64), Email()])
    confirmed = BooleanField('Confirmed')
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Update')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
