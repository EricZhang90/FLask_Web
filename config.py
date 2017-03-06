import os
baseDir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('PW_SECRET_KEY')
    PY_WEB_ADMIN = os.environ.get('PW_WEB_ADMIN')
    PW_POSTS_PER_PAGE = int(os.environ.get('PW_POSTS_PER_PAGE'))

    # DB
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 280
    SQLALCHEMY_POOL_TIMEOUT = 20
    SQLAlCHEMY_COMMIT_ON_TEARDOWN = True
    SECURITY_REGISTERABLE = True
    db_username = os.environ.get('PW_DB_USERNAME')
    db_password = os.environ.get('PW_DB_PASSWORD')
    db_host = os.environ.get('PW_DB_HOST')
    PW_SLOW_DB_QUERY_TIME = 0.5
    SQLALCHEMY_RECORD_QUERIES = True

    # Email
    MAIL_SUBJECT_PREFIX = 'PyWeb'
    MAIL_SENDER = "Eric Zhang <%s>" % os.environ.get('PW_MAIL_USERNAME')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('PW_MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('PW_MAIL_PASSWORD')

    # Performance
    MULTI_THREAD = False
    # It could be true, but the server I am using doesn't support multi-thread.

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

    db_database = os.environ.get('PW_DB_DATABASE')
    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s/%s' % (Config.db_username,
                                                       Config.db_password,
                                                       Config.db_host, db_database)


class TestingConfig(Config):
    TESTING = True

    db_database = os.environ.get('PW_DB_DATABASE')
    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s/%s' % (Config.db_username,
                                                       Config.db_password,
                                                       Config.db_host, db_database)


class ProductionConfig(Config):
    # I DON'T HAVE! HAHAHA
    pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
