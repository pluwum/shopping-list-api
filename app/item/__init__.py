"""This file handles the shopping list item blueprint"""
from flask import Blueprint

# This instance of a Blueprint that represents the shopping list item blueprint
item_blueprint = Blueprint('item', __name__)

from . import views