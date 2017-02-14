import os
baseDir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'Popeyes is better then KFC.'
    SQLAlCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SUBJECT_PREFIX = 'PyWeb'
    MAIL_SENDER = "Eric Zhang <z443655367gmail.com>"
    PY_WEB_ADMIN = os.environ.get('PY_WEB_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # need to set to environment variable later...
    db_username = os.environ.get('PW_DB_USERNAME')
    db_password = os.environ.get('PW_DB_PASSWORD')
    db_host = os.environ.get('PW_DB_HOST')
    db_database = os.environ.get('PW_DB_DATABASE')
    SQLALCHEMY_DATABASE_URI = 'mysql://eric909:zl4166666906@eric909.mysql.pythonanywhere-services.com/eric909$PythonWeb'
    #SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s/%s' % (db_username, db_password, db_host, db_database)


class TestingConfig(Config):
    TESTING = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
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
