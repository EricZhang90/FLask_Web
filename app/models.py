from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
import hashlib



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class AnonymousUser(AnonymousUserMixin):
    def can(self, perminssions):
        return False
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0X04
    MODERATE_COMMENTS = 0X08
    ADMINISTER = 0X80

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administor': (0xff, False)
        }
        for role_name, permision in roles.iteritems():
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
            role.permissions = permision[0]
            role.default = permision[1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

    def __str__(self):
        return self.name

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    _email = db.Column("email", db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    registered_date = db.Column(db.DateTime(), default=datetime.utcnow)
    last_login_date = db.Column(db.DateTime(), default=datetime.utcnow)
    _avatar_hash = db.Column(db.String(32))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self._email == current_app.config['PY_WEB_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
            if self._email is not None and self.avatar_hash is None:
                self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    def __repr__(self):
        return '<User %r>' % self.username

    def __str__(self):
        return self.username

    @property
    def password(self):
        raise AttributeError('Password is not a reable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        db.session.add(self)
        db.session.commit()

    @hybrid_property
    def email(self):
        return self._email

    @hybrid_property
    def avatar_hash(self):
        return self._avatar_hash

    @avatar_hash.setter
    def avatar_hash(self, avatar_hash):
        self._avatar_hash = avatar_hash

    @email.setter
    def email(self, email):
        self._email = email
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        db.session.commit()

    def gravatar(self, size=100, default='mm', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        if self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
            db.session.add(self)
            db.session.commit()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
                url=url, hash=self.avatar_hash, size=size, default=default, rating=rating)

    @classmethod
    def change_password_by_token(cls, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        data = s.loads(token)
        if data.get('user') is None or data.get('password') is None:
            raise ValueError('Invalid Token')
        user = User.query.get(int(data.get('user')))
        if user is None:
            raise ValueError('Invalid Token')
        user.password = data.get('password')

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_change_email_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'user': self.id, 'new_email': new_email})

    def change_email_by_token(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        data = s.loads(token)
        if data.get('user') != self.id or data.get('new_email') is None:
            raise ValueError('Invalid Token')
        self.email = data.get('new_email')

    def generate_reset_password_token(self, password, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'user': self.id, 'password': password})

    def update_last_login_date(self):
        self.last_login_date = datetime.utcnow()
        db.session.add(self)
        db.session.commit()



