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
    SQLALCHEMY_DATABASE_URI = 'mysql://root:4166666906@localhost/PythonWeb'

class TestingConfig(Config):
    TESTING = True
    # TOOO do
    SQLALCHEMY_DATABASE_URI =  ''

class ProductionConfig(Config):
    # I DON'T HAVE! HAHAHA
    pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig

}







