import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config():
    UPLOADS = os.environ.get('UPLOADS') or '/Users/mac/Documents/GitHub/microblog/app/static/images'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'guessedit'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_IMAGE_TYPES = ["","jpg","jpeg","png","gif"]
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['squirrels@authmicroblog.online']
    POSTS_PER_PAGE = 25
    POSTS_PER_PAGE_USERS = 8
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    LANGUAGES = ['en', 'es']

    MAIL_SERVER = 'localhost'
    MAIL_PORT = 587
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_USE_TLS = None  

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,

    'default': Config
}