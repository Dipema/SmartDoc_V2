from flask import Blueprint

bp_publico = Blueprint('publico', __name__)

from . import rutas