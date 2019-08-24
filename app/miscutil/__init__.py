from flask import Blueprint

bp = Blueprint('miscutil', __name__)

from app.miscutil import utils