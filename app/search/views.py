"""This file contains API endpoint logic for the APP"""
from app.decorators import check_logged_in
from app.models import ShoppingList, ShoppingListItem
from flask import jsonify, make_response, request
from flask.views import MethodView
from werkzeug.exceptions import HTTPException, NotFound
from . import search_blueprint


class SearchView(MethodView):
    @check_logged_in
    def get(self, user_id):
        """Add an item to a shopping list
        ---
        tags:
            - "search"
        parameters:
          - name: term
            in: query
            type: string
            required: true
            description: "Search term"
          - name: limit
            in: query
            type: integer
            description: "number of results to display"            
        responses:
            200:
                description: "Search was successful"
            404:
                description: "The page you are looking for does not exist"
            500:
                description: "Something went wrong"
            """
        search_term = str(request.args.get('q', ''))
        limit = int(request.args.get('limit', 10))
        page = int(request.args.get('page', 1))

        try:
            # Search for entry in shopping lists
            shoppinglists = ShoppingList.query.filter(
                ShoppingList.name.ilike("%" + search_term + "%")).filter_by(
                    user_id=user_id).paginate(page, limit)

            results = []
            data = {}

            # Prepare shopping list query results for returning to requestor
            for shoppinglist in shoppinglists.items:
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

            data['meta'] = {
                'has_next': shoppinglists.has_next,
                'has_prev': shoppinglists.has_prev,
                'next_num': shoppinglists.next_num,
                'prev_num': shoppinglists.prev_num,
                'total': shoppinglists.total,
                'page': shoppinglists.page,
                'pages': shoppinglists.pages,
                'per_page': shoppinglists.per_page
            }
            data['data'] = results

            if len(results) == 0:
                # Return a message if search didnot yield any results
                return {
                    "message": "Sorry, your search did not yield any results"
                }, 200

            return make_response(jsonify(data)), 200
        
        except NotFound as e:
            return {
                "message": "The page you are looking for does not exist"
            }, 404
        except Exception as e:
            return {"message": str(e)}, 500


search_view = SearchView.as_view('search_view')

search_blueprint.add_url_rule(
    '/v1/shoppinglists/search/', view_func=search_view, methods=['GET'])
