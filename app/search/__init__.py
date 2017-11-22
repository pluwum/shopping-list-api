"""This file handles the Search blueprint"""
from flask import Blueprint

# This instance of a Blueprint that represents the search blueprint
search_blueprint = Blueprint('search', __name__)

from . import views