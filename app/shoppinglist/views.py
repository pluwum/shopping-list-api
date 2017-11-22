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
from app.decorators import check_logged_in
# Lets initialise our db
db = SQLAlchemy()

# Lets create an instance of the mail App
mail = Mail()


class ShoppinglistsView(MethodView):
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


class ShoppinglistManipulationView(MethodView):
    """Handles Edit, Delete and Show shopping list"""

    @check_logged_in
    def delete(self, user_id, id):
        shoppinglist = ShoppingList.query.filter_by(id=id).first()
        if not shoppinglist:
            # When no shopping list is found, we throw an
            # HTTPException with a 404 not found status code
            return {
                "message": "shoppinglist with id {} not found".format(id)
            }, 404

        if request.method == "DELETE":
            # We handle DELETE the Delete request here
            shoppinglist.delete()
            return {
                "message": "shoppinglist {} deleted".format(shoppinglist.id)
            }, 200

    @check_logged_in
    def get(self, user_id, id):
        shoppinglist = ShoppingList.query.filter_by(id=id).first()
        if not shoppinglist:
            # When no shopping list is found, we throw an
            # HTTPException with a 404 not found status code
            return {
                "message": "shoppinglist with id {} not found".format(id)
            }, 404

        results = []

        # Prepare shopping list query results for returning to
        # requestor
        obj = {
            'id': shoppinglist.id,
            'name': shoppinglist.name,
            'description': shoppinglist.description,
            'date_created': shoppinglist.date_created,
            'date_modified': shoppinglist.date_modified,
            'user_id': shoppinglist.user_id,
            'type': 'list'
        }
        results.append(obj)
        return make_response(jsonify(results)), 200

    @check_logged_in
    def put(self, user_id, id):
        # We handle PUT request to edit list here
        # Grab the name form parameter and save it to the database
        shoppinglist = ShoppingList.query.filter_by(id=id).first()
        if not shoppinglist:
            # When no shopping list is found, we throw an
            # HTTPException with a 404 not found status code
            return {
                "message": "shoppinglist with id {} not found".format(id)
            }, 404

        name = str(request.data.get('name', ''))
        description = str(request.data.get('description', ''))
        shoppinglist.name = name

        if description:
            shoppinglist.description = description
        shoppinglist.save()

        # Now we prepare a response and return it to the requester
        response = {
            'id': shoppinglist.id,
            'name': shoppinglist.name,
            'description': shoppinglist.description,
            'date_created': shoppinglist.date_created,
            'date_modified': shoppinglist.date_modified,
            'user_id': shoppinglist.user_id
        }
        return make_response(jsonify(response)), 200


# Lets make our views callable
shoppinglists_view = ShoppinglistsView.as_view('shoppinglists_view')
shoppinglist_manipulation_view = ShoppinglistManipulationView.as_view(
    'shoppinglist_manipulation_view')

# Then we can add the rules to the blueprint
shoppinglist_blueprint.add_url_rule(
    '/v1/shoppinglists/',
    view_func=shoppinglists_view,
    methods=['POST', 'GET'])

shoppinglist_blueprint.add_url_rule(
    '/v1/shoppinglists/<int:id>',
    view_func=shoppinglist_manipulation_view,
    methods=['GET', 'PUT', 'DELETE'])
