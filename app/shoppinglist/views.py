"""This file contains API endpoint logic for the APP"""

from app.decorators import check_logged_in
from app.models import ShoppingList
from flask import jsonify, make_response, request
from flask.views import MethodView
from . import shoppinglist_blueprint
from app.exceptions import ValueNotFoundError


class ShoppinglistsView(MethodView):
    """Handle Creation and listing of shopping lists"""

    @check_logged_in
    def get(self, user_id):
        # Executes if request is GET
        # Return all shopping list for authed User
        limit = int(request.args.get('limit', 10))
        page = int(request.args.get('page', 1))
        shoppinglists = ShoppingList.get_all(user_id, page, limit)
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
        try:
            name = ShoppingList.verify_name(str(request.data.get('name', '')))
            description = ShoppingList.verify_description(
                str(request.data.get('description', '')))

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
            
        except ValueError as e:
            return {"message": str(e)}, 400
        except TypeError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": str(e)}, 500


class ShoppinglistManipulationView(MethodView):
    """Handles Edit, Delete and Show shopping list"""

    @check_logged_in
    def delete(self, user_id, id):
        try:
            shoppinglist = ShoppingList.get_shopping_list(user_id, id)
            # We handle DELETE the Delete request here
            shoppinglist.delete()
            return {
                "message": "shoppinglist {} deleted".format(shoppinglist.id)
            }, 200
            
        except ValueNotFoundError as e:
            return {"message": str(e)}, 404
        except Exception as e:
            return {"message": str(e)}, 500

    @check_logged_in
    def get(self, user_id, id):
        try:
            shoppinglist = ShoppingList.get_shopping_list(user_id, id)
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

        except ValueNotFoundError as e:
            return {"message": str(e)}, 404
        except Exception as e:
            return {"message": str(e)}, 500

    @check_logged_in
    def put(self, user_id, id):
        # We handle PUT request to edit list here
        # Grab the name form parameter and save it to the database
        try:
            shoppinglist = ShoppingList.get_shopping_list(user_id, id)

            name = ShoppingList.verify_name(str(request.data.get('name', '')))
            description = ShoppingList.verify_description(
                str(request.data.get('description', '')))
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

        except ValueNotFoundError as e:
            return {"message": str(e)}, 404
        except ValueError as e:
            return {"message": str(e)}, 400
        except TypeError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": str(e)}, 500

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
