import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config():
    UPLOADS = os.environ.get('UPLOADS')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_IMAGE_TYPES = ["","jpg","jpeg","png","gif"]
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = (os.environ.get("ADMINS") or 'admin@richardzhang.xyz').split(" ")
    POSTS_PER_PAGE = 25
    POSTS_PER_PAGE_USERS = 8
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
    RESULT_BACKEND = os.environ.get('RESULT_BACKEND')
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    LANGUAGES = ['en', 'es']

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOADS = os.environ.get('UPLOADS')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'madeit'
    ALLOWED_IMAGE_TYPES = ["","jpg","jpeg","png","gif"]

    POSTS_PER_PAGE = 25
    POSTS_PER_PAGE_USERS = 8

    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    RESULT_BACKEND = 'redis://localhost:6379/0'

    MAIL_SERVER = 'localhost'
    MAIL_PORT = 8025
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_USE_TLS = None
    ADMINS = ['admin@richardzhang.xyz']


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