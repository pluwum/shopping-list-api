"""This file contains API endpoint logic for the APP"""
import json
from flask_api import FlaskAPI, status
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from instance.config import app_config
from functools import wraps
# Lets initialise our db
db = SQLAlchemy()

# Lets create an instance of the mail App
mail = Mail()


def create_app(config_name):
    """This wraps our flask app into one function for easy creation of the app
     using our environment config and varying contexts
    """
    from app.models import ShoppingList, User, ShoppingListItem

    # Lets initialize an instance of our flask API
    app = FlaskAPI(__name__, instance_relative_config=True)

    # Lets create an instance of our Bcrytpt extension to overide the default
    bcrypt = Bcrypt(app)

    # Load our flask instance with config from config file
    app.config.from_object(app_config[config_name])

    # Diasble track modifications  reduce performance over head
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    mail.init_app(app)

    # decorator used to allow cross origin requests
    @app.after_request
    def apply_cross_origin_header(response):
        response.headers['Access-Control-Allow-Origin'] = '*'

        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET,HEAD,OPTIONS," \
                                                        "POST,PUT,DELETE"
        response.headers["Access-Control-Allow-Headers"] = "Access-Control-Allow-" \
            "Headers, Origin,Accept, X-Requested-With, Content-Type, " \
            "Access-Control-Request-Method, Access-Control-Request-Headers," \
            "Access-Control-Allow-Origin, Authorization"

        return response

    # Import the required blueprints
    from .auth import auth_blueprint
    from .shoppinglist import shoppinglist_blueprint
    from .item import item_blueprint
    from .search import search_blueprint

    # authentication
    app.register_blueprint(auth_blueprint)

    # shoppinglists
    app.register_blueprint(shoppinglist_blueprint)

    # shopping list items
    app.register_blueprint(item_blueprint)

    # shopping search items ans lists
    app.register_blueprint(search_blueprint)

    return app
