"""This file handles the Shoppinglist blueprint"""
from flask import Blueprint

# This instance of a Blueprint that represents the shoppinglist blueprint
shoppinglist_blueprint = Blueprint('shoppinglist', __name__)

from . import views
