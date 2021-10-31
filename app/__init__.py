from flask import Flask, request
from config import config, Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os, sys
from flask_moment import Moment
from flask_mail import Mail
from celery import Celery
from elasticsearch import Elasticsearch
from flask_assets import Environment, Bundle


celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
moment = Moment()
mail = Mail()
assets = Environment()

def create_app(config_name='default'):

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    celery.conf.update(app.config)

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) if app.config['ELASTICSEARCH_URL'] else None

    assets.init_app(app)
    bundles = {
    'globals_css': Bundle(
        'src/css/styles.css',
        output='css/globals.css',
        filters="postcss"),
    
    'utils_css': Bundle(
        'src/css/upvotejs.css',
        'node_modules/cropperjs/dist/cropper.min.css',
        output='css/utils.css'),

    'bp_css': Bundle(
        'src/css/sidebar_style.css',
        output='css/bp.css',
        filters='postcss'),

    'minigame_css': Bundle(
        'src/minigame/*.css',
        output='css/minigame.css'),

    'globals_js': Bundle(
        'node_modules/jquery/dist/jquery.min.js',
        'node_modules/@popperjs/core/dist/umd/popper.min.js',
        'node_modules/htmx.org/dist/htmx.min.js',
        output='js/globals.js',
        filters='jsmin'),

    'utils_js': Bundle(
        'node_modules/cropperjs/dist/cropper.min.js',
        'src/js/upvotejs.jquery.js',
        'src/js/upvotejs.js',
        output='js/utils.js',
        filters='jsmin'),

    'bp_js': Bundle(
        'src/js/edit_profile.js',
        output='js/bp.js',
        filters='jsmin'),

    'minigame_js': Bundle(
        'src/minigame/*.js',
        output='js/minigame.js',
        filters='jsmin'),
    }
    assets.register(bundles)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.utils import bp as utils_bp
    app.register_blueprint(utils_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.settings import bp as settings_bp
    app.register_blueprint(settings_bp, url_prefix='/settings')

    from app.blog import bp as blog_bp
    app.register_blueprint(blog_bp, url_prefix='/blog')

    from app.explore import bp as explore_bp
    app.register_blueprint(explore_bp)

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        sys.stdout = StreamToLogger(app.logger,logging.INFO)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app

class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, level):
       self.logger = logger
       self.level = level
       self.linebuf = ''

    def write(self, buf):
       for line in buf.rstrip().splitlines():
          self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass

from app import models, email