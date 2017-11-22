"""This file contains API endpoint logic for the APP"""
import json
from flask_api import FlaskAPI, status
from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint, request, jsonify, abort, make_response
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from instance.config import app_config

from flask.views import MethodView
from . import search_blueprint
from app.models import ShoppingList, User, ShoppingListItem
from app.decorators import check_logged_in
# Lets initialise our db
db = SQLAlchemy()


class SearchView(MethodView):
    @check_logged_in
    def get(self, user_id):
        """This section handles the search functionality of the API"""
        search_term = str(request.args.get('q', ''))
        limit = int(request.args.get('limit', 10))
        # TODO: Check if authenticated before search
        # Search for entry in shopping lists
        shoppinglists = ShoppingList.query.filter(
            ShoppingList.name.like("%" + search_term + "%")).limit(limit)

        # Search for entry in shopping list items
        shoppinglist_items = ShoppingListItem.query.filter(
            ShoppingListItem.name.like("%" + search_term + "%")).limit(limit)

        results = []

        # Prepare shopping list query results for returning to requestor
        for shoppinglist in shoppinglists:
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

        # Prepare shopping list item query results for returning to requestor
        for item in shoppinglist_items:
            obj = {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'date_created': item.date_created,
                'date_modified': item.date_modified,
                'shopping_list_id': item.shoppinglist_id,
                'type': 'item'
            }
            results.append(obj)

        if len(results) == 0:
            # Return a message if search didnot yield any results
            return {
                "message": "Sorry, your search did not yield any results"
            }, 200

        return make_response(jsonify(results)), 200


search_view = SearchView.as_view('search_view')

search_blueprint.add_url_rule(
    '/v1/shoppinglists/search/', view_func=search_view, methods=['GET'])
