from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
import hashlib
from markdown import markdown
import bleach


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0X04
    MODERATE_COMMENTS = 0X08
    ADMINISTER = 0X80


class AnonymousUser(AnonymousUserMixin):
    def can(self, perminssions):
        return False
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


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


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_fake_data(count=100):
        from random import seed, randint
        from sqlalchemy.exc import IntegrityError
        seed()
        user_count = User.query.count()
        i = 0
        while i < count:
            follower_offset = randint(0, user_count - 1)
            followed_offset = randint(0, user_count - 1)
            if follower_offset == followed_offset:
                continue
            i += 1
            follower = User.query.offset(follower_offset).first()
            followed = User.query.offset(followed_offset).first()
            try:
                follower.follow(followed)
            except IntegrityError:
                db.session.rollback()



class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    _email = db.Column("email", db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    _password_hash = db.Column("password_hash", db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    registered_date = db.Column(db.DateTime(), default=datetime.utcnow)
    last_login_date = db.Column(db.DateTime(), default=datetime.utcnow)
    _avatar_hash = db.Column("avatar_hash", db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self._email == current_app.config['PY_WEB_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
#        if self._email is not None and self.avatar_hash is None:
#            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    @hybrid_property
    def password(self):
        raise AttributeError('Password is not a reable attribute')

    @password.setter
    def password(self, password):
        self._password_hash = generate_password_hash(password)
        db.session.add(self)
        db.session.commit()

    @hybrid_property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        self._email = email
        self._avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        db.session.commit()

    @hybrid_property
    def avatar_hash(self):
        return self._avatar_hash

    @avatar_hash.setter
    def avatar_hash(self, avatar_hash):
        self._avatar_hash = avatar_hash
        db.session.add(self)
        db.session.commit()

    @hybrid_property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id==Post.author_id)\
                         .filter(Follow.follower_id==self.id)

    def __repr__(self):
        return '<User %r>' % self.username

    def __str__(self):
        return self.username

    def gravatar(self, size=100, default='identicon', rating='g'):
        if self.is_administrator():
            default = 'mm'
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        if self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
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
        return check_password_hash(self._password_hash, password)

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

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None


    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def follow(self, user):
        if self.is_following(user) == False:
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    @staticmethod
    def follow_self():
        for user in User.query.all():
            user.follow(user)

    @staticmethod
    def generate_fake_data(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()
        for i in range(count):
            u = User(_email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     _password_hash=generate_password_hash(forgery_py.lorem_ipsum.word()),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     registered_date=forgery_py.date.date(True))
            try:
                db.session.add(u)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)

    @staticmethod
    def generate_fake_data(count=100):
        from random import seed, randint
        import forgery_py
        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1,3)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
                                            markdown(value, output_format='html'),
                                            tags=allowed_tags,
                                            strip=True)) # Hide the tags isn't in whitelist.


db.event.listen(Post.body, 'set', Post.on_changed_body)






