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
from . import item_blueprint
from app.models import ShoppingList, User, ShoppingListItem
from app.decorators import check_logged_in
# Lets initialise our db
db = SQLAlchemy()

# Lets create an instance of the mail App
mail = Mail()


class ItemView(MethodView):
    @check_logged_in
    def get(self, user_id, id):
        shoppinglist = ShoppingList.query.filter_by(id=id).first()
        if not shoppinglist:
            # When no shopping list is found, we throw an error
            return {"message": "Sorry, this shopping list doesnt exist"}, 404

        # Handdle GET View list/Show list request here
        shoppinglist_items = ShoppingListItem.query.filter_by(
            shoppinglist_id=shoppinglist.id)

        results = []

        # Prepare shopping list item query results for returning
        # to requestor
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
            return {"message": "Sorry, this shopping list is empty"}, 404
        return make_response(jsonify(results)), 200

    @check_logged_in
    def post(self, user_id, id):
        shoppinglist = ShoppingList.query.filter_by(id=id).first()
        if not shoppinglist:
            # When no shopping list is found, we throw an error
            return {"message": "Sorry, this shopping list doesnt exist"}, 404

        # Go ahead and handle the request, since the user is authed
        name = str(request.data.get('name', ''))
        description = str(request.data.get('description', ''))
        if name:
            # Create a shopping list item model and persist it
            shoppinglist_item = ShoppingListItem(
                name=name, shoppinglist_id=id, description=description)
            shoppinglist_item.save()

            # Prepare a response and return it to the requestor
            response = jsonify({
                'id':
                shoppinglist_item.id,
                'name':
                shoppinglist_item.name,
                'description':
                shoppinglist_item.description,
                'date_created':
                shoppinglist.description,
                'date_created':
                shoppinglist_item.date_created,
                'date_modified':
                shoppinglist_item.date_modified,
                'user_id':
                user_id,
                'shoppinglist_id':
                id
            })
            return make_response(response), 201


class ItemManipulationView(MethodView):
    @check_logged_in
    def delete(self, user_id, id, item_id):
        shoppinglist_item = ShoppingListItem.query.filter_by(
            id=item_id).first()
        if not shoppinglist_item:
            # When item model isn't found, Raise an HTTPException
            # With a 404 not found status code
            return {
                "message": "Sorry, this shopping list item doesnt exist"
            }, 404
        # When model is found, Handle delete here
        shoppinglist_item.delete()

        # Return reponse to requestor
        return {
            "message": "shoppinglist item {} deleted".format(
                shoppinglist_item.id)
        }, 200

    @check_logged_in
    def put(self, user_id, id, item_id):
        # Handle Editing of item here

        shoppinglist_item = ShoppingListItem.query.filter_by(
            id=item_id).first()
        if not shoppinglist_item:
            # When item model isn't found, Raise an HTTPException
            # With a 404 not found status code
            return {
                "message": "Sorry, this shopping list item doesnt exist"
            }, 404
        # Grab new item name as string and pass it to the database
        name = str(request.data.get('name', ''))
        description = str(request.data.get('description', ''))
        shoppinglist_item.name = name
        if (description):
            shoppinglist_item.description = description
        shoppinglist_item.save()

        # Prepare response and return it to the user
        response = {
            'id': shoppinglist_item.id,
            'name': shoppinglist_item.name,
            'description': shoppinglist_item.description,
            'date_created': shoppinglist_item.date_created,
            'date_modified': shoppinglist_item.date_modified,
            'user_id': user_id,
            'shoppinglist_id': id
        }
        return make_response(jsonify(response)), 200


item_view = ItemView.as_view('item_view')
item_manipulation_view = ItemManipulationView.as_view('item_manipulation_view')

item_blueprint.add_url_rule(
    '/v1/shoppinglists/<int:id>/items',
    view_func=item_view,
    methods=['POST', 'GET'])

item_blueprint.add_url_rule(
    '/v1/shoppinglists/<int:id>/items/<int:item_id>',
    view_func=item_manipulation_view,
    methods=['PUT', 'DELETE'])
