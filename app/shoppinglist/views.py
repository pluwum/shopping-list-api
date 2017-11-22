"""This file contains API endpoint logic for the APP"""
import json
from flask_api import FlaskAPI, status
from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint, request, jsonify, abort, make_response
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from instance.config import app_config
from functools import wraps

from flask.views import MethodView
from . import shoppinglist_blueprint
from app.models import ShoppingList, User, ShoppingListItem
# Lets initialise our db
db = SQLAlchemy()

# Lets create an instance of the mail App
mail = Mail()


def check_logged_in(function):
    @wraps(function)
    def wrapper(self, *args, **kwargs):
        # Get token authentication information from header
        auth_header = request.headers.get('Authorization')
        message = "Not permited because Authorization header not " \
            "provided with this request!"
        if auth_header is not None:
            # Split Bearer and token then grab the token
            access_token = auth_header.split(" ")[1]

            if access_token:
                # Decode user info from jwt hashed token
                user_id = User.decode_token(access_token)

                # Check if user is user is authenticated
                if not isinstance(user_id, str):
                    return function(self, user_id, *args, **kwargs)
                else:
                    message = user_id
        return {"message": message}, 401

    return wrapper


class ShoppinglistView(MethodView):
    """Handle Creation and listing of shopping lists"""

    @check_logged_in
    def get(self, user_id):
        # Executes if request is GET
        # Return all shopping list for authed User
        shoppinglists = ShoppingList.get_all(user_id)
        results = []

        for shoppinglist in shoppinglists:
            obj = {
                'id': shoppinglist.id,
                'name': shoppinglist.name,
                'description': shoppinglist.description,
                'date_created': shoppinglist.date_created,
                'date_modified': shoppinglist.date_modified,
                'user_id': shoppinglist.user_id
            }
            results.append(obj)

        # Return reponse with shopping lists and set server code
        return make_response(jsonify(results)), 200

    @check_logged_in
    def post(self, user_id):
        name = str(request.data.get('name', ''))
        description = str(request.data.get('description', ''))
        if name:
            shoppinglist = ShoppingList(
                name=name, user_id=user_id, description=description)
            shoppinglist.save()
            response = jsonify({
                'id': shoppinglist.id,
                'name': shoppinglist.name,
                'description': shoppinglist.description,
                'date_created': shoppinglist.date_created,
                'date_modified': shoppinglist.date_modified,
                'user_id': user_id
            })

            return make_response(response), 201
        else:
            message = "Name field not passed with request."\
                "Please try again"
            response = {'message': message}
            return make_response(jsonify(response)), 200


# Lets make our views callable
shoppinglist_view = ShoppinglistView.as_view('shoppinglist_view')

# Add the rule for the shoppinglist end point  /auth/register
# Then we can add the rule to the blueprint
shoppinglist_blueprint.add_url_rule(
    '/v1/shoppinglists/', view_func=shoppinglist_view, methods=['POST', 'GET'])