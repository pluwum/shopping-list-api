"""This file contains API endpoint logic for the APP"""
from app.decorators import check_logged_in
from app.models import ShoppingList, ShoppingListItem
from flask import jsonify, make_response, request
from flask.views import MethodView
from app.exceptions import ValueNotFoundError
from . import item_blueprint


class ItemView(MethodView):
    @check_logged_in
    def get(self, user_id, id):
        try:
            shoppinglist = ShoppingList.get_shopping_list(user_id, id)

            limit = int(request.args.get('limit', 10))
            page = int(request.args.get('page', 1))

            # Handdle GET View list/Show list request here
            shoppinglist_items = ShoppingListItem.get_all(id, page, limit)

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

            return make_response(jsonify(results)), 200

        except ValueNotFoundError as e:
            return {"message": str(e)}, 404
        except Exception as e:
            return {"message": str(e)}, 500

    @check_logged_in
    def post(self, user_id, id):
        try:
            shoppinglist = ShoppingList.get_shopping_list(user_id, id)

            # Go ahead and handle the request, since the user is authed
            name = ShoppingList.verify_name(str(request.data.get('name', '')))
            description = ShoppingList.verify_description(
                str(request.data.get('description', '')))

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
                shoppinglist_item.date_created,
                'date_modified':
                shoppinglist_item.date_modified,
                'user_id':
                user_id,
                'shoppinglist_id':
                id
            })
            return make_response(response), 201

        except ValueNotFoundError as e:
            return {"message": str(e)}, 404
        except ValueError as e:
            return {"message": str(e)}, 400
        except TypeError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": str(e)}, 500


class ItemManipulationView(MethodView):
    @check_logged_in
    def delete(self, user_id, id, item_id):
        try:
            shoppinglist = ShoppingList.get_shopping_list(user_id, id)

            shoppinglist_item = ShoppingListItem.get_shopping_list_item(
                item_id)

            # When model is found, Handle delete here
            shoppinglist_item.delete()

            # Return reponse to requestor
            return {
                "message":
                "shoppinglist item {} deleted".format(shoppinglist_item.id)
            }, 200

        except ValueNotFoundError as e:
            return {"message": str(e)}, 404
        except Exception as e:
            return {"message": str(e)}, 500

    @check_logged_in
    def put(self, user_id, id, item_id):
        try:
            # Handle Editing of item here
            shoppinglist = ShoppingList.get_shopping_list(user_id, id)

            shoppinglist_item = ShoppingListItem.get_shopping_list_item(
                item_id)

            # Grab new item name as string and pass it to the database
            name = ShoppingList.verify_name(str(request.data.get('name', '')))
            description = ShoppingList.verify_description(
                str(request.data.get('description', '')))

            shoppinglist_item.name = name
            if description:
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

        except ValueNotFoundError as e:
            return {"message": str(e)}, 404
        except ValueError as e:
            return {"message": str(e)}, 400
        except TypeError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": str(e)}, 500


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
