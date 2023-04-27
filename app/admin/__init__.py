from flask import Blueprint

bp_admin = Blueprint('admin', __name__)

from . import rutas