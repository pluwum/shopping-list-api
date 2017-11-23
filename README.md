[![Code Climate](https://codeclimate.com/github/codeclimate/codeclimate/badges/gpa.svg)](https://codeclimate.com/github/pluwum/shopping-list-api)
[![Test Coverage](https://codeclimate.com/github/codeclimate/codeclimate/badges/coverage.svg)](https://codeclimate.com/github/pluwum/shopping-list-api)
[![Build Status](https://travis-ci.org/pluwum/shopping-list-api.svg?branch=master)](https://travis-ci.org/pluwum/shopping-list-api)
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
POST /shoppinglists/  | name, description | JSON
GET /shoppinglists/  | | JSON
GET /shoppinglists/<id>  | | JSON
PUT /shoppinglists/<id>  | name, description | JSON
DELETE /shoppinglists/<id>  | | JSON
GET/shoppinglists/<id>/items/  | | JSON
POST /shoppinglists/<id>/items/  | name, description | JSON
PUT /shoppinglists/<id>/items/<item_id>  | name, description |JSON
DELETE /shoppinglists/<id>/items/<item_id> | | JSON
GET /shoppinglists/search/q=<serach_term> | | JSON

# Motivation

This project is part of a submission for week two of Andela BootCamp UG CH3 2017. All the features available are developed as specified by the assignment
# Installation
1. Install postgresql. Click [here](https://labkey.org/Documentation/wiki-page.view?name=installPostgreSQLWindows) for installation instructions

2. Create the databases
  - `psql -c 'create database test_db;' -U postgres`
  - `psql -c 'create database shoppinglist;' -U postgres`

3. Setup a virtual environment

4. Install the required packages
    pip -r install requirements.txt

5. Setup the DB using the manage.py script

    `python manage.py db init`

    `python manage.py db migrate`

    `python manage.py db upgrade`

6. Run the application

    `python run.py`

# Tests

The tests are contained in the `/tests` folder. After installing the PyTest dependency, you can run them  all as below:

    `python -m pytest tests/`

# Contributors

Shout out to [myself](https://github.com/pluwum)