# shopping-list-api
This project is a RESTful API using Flask with Endpoints that:
- a. Enable users to create accounts and login into the application 
- b. Enable users to create, update, view and delete a shopping list
- c. Add, update, view or delete items in a shopping list

# Usage
The API can be accessed using the following end points

END POINT|PARAM|RESPONSE
----------|------|--------
POST /auth/register|email, password | JSON
POST /auth/login  | email, password | JSON
POST /auth/logout | | JSON
POST /auth/reset-password  | email | JSON
POST /shoppinglists/  | name | JSON
GET /shoppinglists/  | | JSON
GET /shoppinglists/<id>  | | JSON
PUT /shoppinglists/<id>  | | JSON
DELETE /shoppinglists/<id>  | | JSON
POST /shoppinglists/<id>/items/  | | JSON
PUT /shoppinglists/<id>/items/<item_id>  | |JSON
DELETE /shoppinglists/<id>/items/<item_id> | | JSON

# Motivation

This project is part of a submission for week two of Andela BootCamp UG CH3 2017. All the features available are development as specified by the assignment
# Installation

1. First: Install the required packages
    pip -r install requirements.txt

2. Secondly: Setup the DB using the manage.py script

`python manage.py db init`

`python manage.py db migrate`

`python manage.py db upgrade`

3. Thirdly: Run the application

`python run.py`

# Tests

The tests are contained in the `/tests` folder. After installing the PyTest dependency, you can run them  all as below:
`python -m pytest tests/`

# Contributors

Shout out to [myself](https://github.com/pluwum)