"""This file contains API endpoint logic for the APP"""
import json
from flask_api import FlaskAPI, status
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response
from flask_bcrypt import Bcrypt
from instance.config import app_config

# Lets initialise our db
db = SQLAlchemy()


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

    @app.route('/shoppinglists/', methods=['POST', 'GET'])
    def shoppinglists():
        """Handle Creation and listing of shopping lists"""
        # Get token authentication information from header
        auth_header = request.headers.get('Authorization')
        # Split Bearer and token then grab the token
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Decode user info from jwt hashed token
            user_id = User.decode_token(access_token)

            # Check if user is user is authenticated
            if not isinstance(user_id, str):
                # Lets Go a head and handle the request, the user is authed
                if request.method == "POST":
                    name = str(request.data.get('name', ''))
                    if name:
                        shoppinglist = ShoppingList(name=name, user_id=user_id)
                        shoppinglist.save()
                        response = jsonify({
                            'id': shoppinglist.id,
                            'name': shoppinglist.name,
                            'date_created': shoppinglist.date_created,
                            'date_modified': shoppinglist.date_modified,
                            'user_id': user_id
                        })

                        return make_response(response), 201
                    else:
                        message = "Name field not passed with request."\
                            "Please try again"
                        response = {
                            'message': message
                        }
                        return make_response(jsonify(response)), 200
                else:
                    # Executes if request is GET
                    # Return all shopping list for authed User
                    shoppinglists = ShoppingList.get_all(user_id)
                    results = []

                    for shoppinglist in shoppinglists:
                        obj = {
                            'id': shoppinglist.id,
                            'name': shoppinglist.name,
                            'date_created': shoppinglist.date_created,
                            'date_modified': shoppinglist.date_modified,
                            'user_id': shoppinglist.user_id
                        }
                        results.append(obj)

                    # Return reponse with shopping lists and set server code
                    return make_response(jsonify(results)), 200
            else:
                # Executes when user is not authorized
                # Return the message returned by the jwt decode function
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

    @app.route('/shoppinglists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def shoppinglist_manipulation(id, **kwargs):
        """Handles Edit, Delete and Show shopping list"""

        # Get token authentication information from header
        auth_header = request.headers.get('Authorization')
        # Split Bearer and token then grab the token
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Decode user info from jwt hashed token
            user_id = User.decode_token(access_token)

            # Check if user is authenticated
            if not isinstance(user_id, str):
                # Since user is authenticated, lets Handle this request
                shoppinglist = ShoppingList.query.filter_by(id=id).first()
                if not shoppinglist:
                    # When no shopping list is found, we throw an
                    # HTTPException with a 404 not found status code
                    abort(404)

                if request.method == "DELETE":
                    # We handle DELETE the Delete request here
                    shoppinglist.delete()
                    return {
                        "message":
                        "shoppinglist {} deleted".format(shoppinglist.id)
                    }, 200
                elif request.method == 'PUT':
                    # We handle PUT request to edit list here
                    # Grab the name form parameter and save it to the database
                    name = str(request.data.get('name', ''))
                    shoppinglist.name = name
                    shoppinglist.save()

                    # Now we prepare a response and return it to the requester
                    response = {
                        'id': shoppinglist.id,
                        'name': shoppinglist.name,
                        'date_created': shoppinglist.date_created,
                        'date_modified': shoppinglist.date_modified,
                        'user_id': shoppinglist.user_id
                    }
                    return make_response(jsonify(response)), 200
                else:
                    # Handdle GET View list/Show list request here
                    # We prepare a response with model info & return it
                    response = jsonify({
                        'id': shoppinglist.id,
                        'name': shoppinglist.name,
                        'date_created': shoppinglist.date_created,
                        'date_modified': shoppinglist.date_modified,
                        'user_id': shoppinglist.user_id
                    })
                    return make_response(response), 200
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

    @app.route('/shoppinglists/<int:id>/items', methods=['POST'])
    def shoppinglist_items(id):
        """ This will add items to the shopping list with specified <id>"""
        # Get token authentication information from header
        auth_header = request.headers.get('Authorization')
        # Split Bearer and token then grab the token
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Decode user info from jwt hashed token
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, since the user is authed
                name = str(request.data.get('name', ''))
                if name:
                    # Create a shopping list item model and persist it the DB
                    shoppinglist_item = ShoppingListItem(
                        name=name, shoppinglist_id=id)
                    shoppinglist_item.save()

                    # Prepare a response and return it to the requestor
                    response = jsonify({
                        'id': shoppinglist_item.id,
                        'name': shoppinglist_item.name,
                        'date_created': shoppinglist_item.date_created,
                        'date_modified': shoppinglist_item.date_modified,
                        'user_id': user_id,
                        'shoppinglist_id': id
                    })
                    return make_response(response), 201
            else:
                # User is not authenticated so return message from JWT decode()
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

    @app.route('/shoppinglists/<int:id>/items/<int:item_id>',
               methods=['PUT', 'DELETE'])
    def shoppinglist_item_manipulation(id, item_id):
        """ This handles EDIT and DELETE shopping list item actions"""

        # Get token authentication information from header
        auth_header = request.headers.get('Authorization')
        # Split Bearer and token then grab the token
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Decode user info from JWT hashed token
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                shoppinglist_item = ShoppingListItem.query.filter_by(
                    id=item_id).first()
                if not shoppinglist_item:
                    # When item model isn't found, Raise an HTTPException
                    # With a 404 not found status code
                    abort(404)

                if request.method == "DELETE":
                    # When model is found, Handle delete here
                    shoppinglist_item.delete()

                    # Return reponse to requestor
                    return {
                        "message":
                        "shoppinglist item {} deleted".format(
                            shoppinglist_item.id)
                    }, 200
                elif request.method == 'PUT':
                    # Handle Editing of item here
                    # Grab new item name as string and pass it to the database
                    name = str(request.data.get('name', ''))
                    shoppinglist_item.name = name
                    shoppinglist_item.save()

                    # Prepare response and return it to the user
                    response = {
                        'id': shoppinglist_item.id,
                        'name': shoppinglist_item.name,
                        'date_created': shoppinglist_item.date_created,
                        'date_modified': shoppinglist_item.date_modified,
                        'user_id': user_id,
                        'shoppinglist_id': id
                    }
                    return make_response(jsonify(response)), 200
            else:
                # When user is not authenticated. Prepare response and return
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

    @app.route('/shoppinglists/search/', methods=['GET'])
    def shoppinglist_search():
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

    # import the authentication blueprint and register it to our the app
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
