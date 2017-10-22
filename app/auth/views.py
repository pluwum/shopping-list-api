"""This file contains the API logic for handling Auhtentication based requests
for registration and login
"""
from app.models import BlacklistToken, User
from flask import Blueprint, jsonify, make_response, request
from flask.views import MethodView

from . import auth_blueprint


class RegistrationView(MethodView):
    """This class registers a new user."""

    def post(self):
        """Handle POST requests for the registration endpoint"""

        # lets check if the user already exists
        user = User.query.filter_by(email=request.data['email']).first()

        if not user:
            # This user doesn't exist, so lets create them
            try:
                # Grab email and password and save them to the database
                post_data = request.data
                email = post_data['email']
                password = post_data['password']
                user = User(email=email, password=password)
                user.save()

                # Return success response to the requestor
                response = {
                    'message': 'You registered successfully. Please log in.'
                }
                return make_response(jsonify(response)), 201
            except Exception as e:
                # Return to requestor a message with the error that occured
                response = {'message': str(e)}
                return make_response(jsonify(response)), 401
        else:
            # This handles a case where user already exists
            # Return am message telling them it already exist
            response = {'message': 'User already exists. Please login.'}

            return make_response(jsonify(response)), 202


class PasswordResetView(MethodView):
    """This handles password reset action"""

    def post(self):
        """This handles POST requests for password reset"""
        # TODO: implement this
        response = {'message': 'You reset password successfully.'}

        return make_response(jsonify(response)), 200


class LogoutView(MethodView):
    """This handles logout action"""

    def post(self):
        # get access token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            access_token = auth_header.split(" ")[1]
        else:
            access_token = ''
        if access_token:
            resp = User.decode_token(access_token)
            if not isinstance(resp, str):
                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=access_token)
                try:
                    # insert the token into the blacklist table
                    blacklist_token.save()
                    response = {"message": 'Successfully logged out.'}
                    return make_response(jsonify(response)), 200
                except Exception as e:
                    response = {"message": str(e)}
                    return make_response(jsonify(response)), 200
            else:
                response = {"message": resp}
                return make_response(jsonify(response)), 401
        else:
            response = {"message": 'Provide a valid auth token.'}
            return make_response(jsonify(response)), 403


class LoginView(MethodView):
    """This view handles user login action."""

    def post(self):
        """Handle POST request for this view. Url ---> /auth/login"""
        try:
            # Get the user model from DB by email
            user = User.query.filter_by(email=request.data['email']).first()

            # Try to authenticate the found user using their password
            if user and user.password_is_valid(request.data['password']):

                # Generate the access token for authentication
                access_token = user.generate_token(user.id)
                if access_token:
                    response = {
                        'message': 'You logged in successfully.',
                        'access_token': access_token.decode()
                    }
                    return make_response(jsonify(response)), 200
            else:
                # This User doesn't exist so lets return an error message
                response = {
                    'message': 'Invalid email or password, Please try again'
                }
                return make_response(jsonify(response)), 401

        except Exception as e:
            # Prepare and send a response with the error that has occured
            response = {'message': str(e)}
            # Return the using the HTTP Error Code 500 (Internal Server Error)
            return make_response(jsonify(response)), 500


# Lets make our rauth views callable
registration_view = RegistrationView.as_view('registration_view')
login_view = LoginView.as_view('login_view')
logout_view = LogoutView.as_view('logout_view')
password_reset_view = PasswordResetView.as_view('password_reset_view')

# Add the rule for the registration end point  /auth/register
# Then we can add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/auth/register', view_func=registration_view, methods=['POST'])

# Define the rule for the login endpoint  /auth/login
# And then we add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/auth/login', view_func=login_view, methods=['POST'])

# Define the rule for the logout endpoint  /auth/logout
# And then we add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/auth/logout', view_func=logout_view, methods=['POST'])

# Define the rule for the logout endpoint  /auth/reset-password
# And then we add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/auth/reset-password', view_func=password_reset_view, methods=['POST'])
