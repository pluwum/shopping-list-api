import json
from flask_api import FlaskAPI, status
from flask_sqlalchemy import SQLAlchemy

from flask import request, jsonify, abort, make_response

# local import

from instance.config import app_config

# For password hashing
from flask_bcrypt import Bcrypt

# initialize db
db = SQLAlchemy()


def create_app(config_name):

    from app.models import ShoppingList, User, ShoppingListItem

    app = FlaskAPI(__name__, instance_relative_config=True)
    # overriding Werkzeugs built-in password hashing utilities using Bcrypt.
    bcrypt = Bcrypt(app)

    app.config.from_object(app_config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/shoppinglists/', methods=['POST', 'GET'])
    def shoppinglists():
        # get the access token
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authed
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
                    # GET
                    # get all the shoppinglists for this user
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

                    return make_response(jsonify(results)), 200
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

    @app.route('/shoppinglists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def shoppinglist_manipulation(id, **kwargs):

        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                shoppinglist = ShoppingList.query.filter_by(id=id).first()
                if not shoppinglist:
                    # Raise an HTTPException with a 404 not found status code
                    abort(404)

                if request.method == "DELETE":
                    shoppinglist.delete()
                    return {
                        "message": "shoppinglist {} deleted".format(shoppinglist.id)
                    }, 200
                elif request.method == 'PUT':
                    name = str(request.data.get('name', ''))
                    shoppinglist.name = name
                    shoppinglist.save()
                    response = {
                        'id': shoppinglist.id,
                        'name': shoppinglist.name,
                        'date_created': shoppinglist.date_created,
                        'date_modified': shoppinglist.date_modified,
                        'user_id': shoppinglist.user_id
                    }
                    return make_response(jsonify(response)), 200
                else:
                    # GET
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

    # Lets add items to the list with <id>
    @app.route('/shoppinglists/<int:id>/items', methods=['POST'])
    def shoppinglist_items(id):
        # get the access token
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authed
                if request.method == "POST":
                    name = str(request.data.get('name', ''))
                    if name:
                        shoppinglist_item = ShoppingListItem(
                            name=name, shoppinglist_id=id)
                        shoppinglist_item.save()
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
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

    # Edit Or Delete list items
    @app.route('/shoppinglists/<int:id>/items/<int:item_id>', methods=['PUT', 'DELETE'])
    def shoppinglist_item_manipulation(id, item_id):

        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                shoppinglist_item = ShoppingListItem.query.filter_by(
                    id=item_id).first()
                if not shoppinglist_item:
                    # Raise an HTTPException with a 404 not found status code
                    abort(404)

                if request.method == "DELETE":
                    shoppinglist_item.delete()
                    return {
                        "message": "shoppinglist item {} deleted".format(shoppinglist_item.id)
                    }, 200
                elif request.method == 'PUT':
                    name = str(request.data.get('name', ''))
                    shoppinglist_item.name = name
                    shoppinglist_item.save()
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
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

    @app.route('/shoppinglists/search/', methods=['GET'])
    def shoppinglist_search():
        search_term = str(request.args.get('q', ''))
        limit = int(request.args.get('limit', 10))
        # TODO: Check if authenticated before search
        shoppinglists = ShoppingList.query.filter(ShoppingList.name.like("%"+search_term+"%")).limit(limit)
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

        if len(results) == 0:
            return {
                        "message": "No records found"
                    }, 200

        return make_response(jsonify(results)), 200

    # import the authentication blueprint and register it on the app
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
