from flask import Blueprint

bp = Blueprint('utils', __name__)

from app.utils import utils