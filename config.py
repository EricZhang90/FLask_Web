import os
baseDir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('PW_SECRET_KEY')
    SQLAlCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SUBJECT_PREFIX = 'PyWeb'
    MAIL_SENDER = "Eric Zhang <z443655367gmail.com>"
    PY_WEB_ADMIN = os.environ.get('PW_WEB_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 280
    SQLALCHEMY_POOL_TIMEOUT = 20
    SECURITY_REGISTERABLE = True

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('PW_MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('PW_MAIL_PASSWORD')

    db_username = os.environ.get('PW_DB_USERNAME')
    db_password = os.environ.get('PW_DB_PASSWORD')
    db_host = os.environ.get('PW_DB_HOST')
    db_database = os.environ.get('PW_DB_DATABASE')
    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s/%s' % (db_username, db_password, db_host, db_database)

class TestingConfig(Config):
    TESTING = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('PW_MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('PW_MAIL_PASSWORD')
    db_username = os.environ.get('PW_DB_USERNAME')
    db_password = os.environ.get('PW_DB_PASSWORD')
    db_host = os.environ.get('PW_DB_HOST')
    db_database = os.environ.get('PW_DB_DATABASE')
    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s/%s' % (db_username, db_password, db_host, db_database)


class ProductionConfig(Config):
    # I DON'T HAVE! HAHAHA
    pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig

}
