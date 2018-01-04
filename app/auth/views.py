"""This file contains the API logic for handling Auhtentication based requests
for registration and login
"""
import uuid

from app import mail
from app.models import BlacklistToken, User
from flask import jsonify, make_response, request
from flask.views import MethodView
from flask_mail import Message

from . import auth_blueprint


class RegistrationView(MethodView):
    def post(self):
        """Registration of a new user
        ---
        tags:
            - "auth"
        parameters:
          - in: "body"
            name: "body"
            description: "password, email"
            required: true
            schema:
             type: "object"
             required:
             - "password"
             - "email"
             properties:
              password:
               type: "string"
              email:
               type: "string"
        responses:
            201:
                description: "Successfully Registerd"
            409:
                description: "Failed to register, duplicate user"
            400:
                description: "Failed to register, Invalid data supplied"
            500:
                description: "Failed to register, Something went wrong"
            """
        # lets check if the user already exists
        try:
            email = User.verify_username(request.data['email'])
            password = User.verify_password(request.data['password'])
        except ValueError as e:
            return {"message": str(e)}, 400
        except TypeError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": str(e)}, 500

        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                # Grab email and password and save them to the database
                user = User(email=email, password=password)
                user.save()

                # Return success response to the requestor
                response = {
                    'message': 'You registered successfully. Please log in.'
                }
                return make_response(jsonify(response)), 201

            else:
                # This handles a case where user already exists
                # Return am message telling them it already exist
                response = {'message': 'User already exists. Please login.'}
                return {"message": 'User already exists. Please login.'}, 409

        except Exception as e:
            # Return to requestor a message with the error that occured
            return {"message": str(e)}, 500


class PasswordResetView(MethodView):
    """This handles password reset request action"""

    def post(self):
        """Request for a user's password reset
        ---
        tags:
            - "auth"
        parameters:
          - in: "body"
            name: "email"
            description: "user's email address"
            required: true
            schema:
             type: "object"
             required:
             - "email"
             properties:
              email:
               type: "string"
        responses:
            200:
                description: "Reset email was Successfully sent"
            404:
                description: "User doesnt exist in the system."
            400:
                description: "Failed to register, Invalid data supplied"
            500:
                description: "Failed to reset because something went wrong"
            """

        # lets check if the user exists
        try:
            email = User.verify_username(request.data['email'])
            user = User.query.filter_by(email=email).first()
            access_token = user.generate_token(user.id)
        except ValueError as e:
            return {"message": str(e)}, 400
        except TypeError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": str(e)}, 500

        if user and access_token:
            # Prepare email to send to the user
            msg = Message(
                "Shopping list API Password Reset",
                sender="Shopping List API<test.mail.ug@gmail.com",
                recipients=["luwyxx@gmail.com"])
            msg.html = "Hello, click <a href='{}?auth_token={}'>here</a> to reset your \
            password. If you didnt not request this please ignore".format(
                request.base_url, access_token.decode())

            try:
                mail.send(msg)
                response = {
                    'message':
                    'You request for password reset has been received. Check your email \
                    for a reset link'
                }
                return make_response(jsonify(response)), 200
            except Exception as e:
                response = {'message': str(e)}
                return make_response(jsonify(response)), 500
        else:
            response = {'message': 'User doesnt exist in the system.'}
            return make_response(jsonify(response)), 404

    def get(self):
        """Reset a user's password
        ---
        tags:
            - "auth"
        responses:
            200:
                description: "User password was successfully reset"
            401:
                description: "Sorry, temporary access token not found"
            500:
                description: "Failed to reset because something went wrong"
            """
        # Split Bearer and token then grab the token
        access_token = str(request.args.get('auth_token', ''))

        if not access_token:
            return {"message": "Sorry, temporary access token not found"}, 401

        # Decode user info from jwt hashed token
        user_id = User.decode_token(access_token)

        # Check if user is authenticated
        if not isinstance(user_id, str):
            user = User.query.filter_by(id=user_id).first()
            # Lets generate some string to use as the new password
            password = str(uuid.uuid4())
            password.replace("-", "")
            password = password[0:8]
            user.password = user.hash_password(password)
            user.save()

            # Lets prepare the email content
            msg = Message(
                "Shopping list API Password Reset",
                sender="Shopping List API<test.mail.ug@gmail.com",
                recipients=["luwyxx@gmail.com"])
            msg.html = "Your password was succesfully reset, you can use \
            <b>{}</b> to login".format(password)
            # Lets send the email
            try:
                mail.send(msg)
                # blacklist the token used
                blacklist_token = BlacklistToken(token=access_token)
                blacklist_token.save()

                response = {
                    'message':
                    'You reset password for {} successfully.'.format(
                        user.email)
                }
                return make_response(jsonify(response)), 200
            except Exception as e:
                response = {
                    'message':
                    'Sorry, we failed to send your password reset email.'
                }
                return make_response(jsonify(response)), 500


class LogoutView(MethodView):
    """This handles logout action"""

    def post(self):
        """Logout a logged in user
        ---
        tags:
            - "auth"
        responses:
            200:
                description: "User uccessfully logged out."
            401:
                description: "Invalid Auth token Provided."
            500:
                description: "Failed to logout because something went wrong"
            """
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
                    return make_response(jsonify(response)), 500
            else:
                response = {"message": resp}
                return make_response(jsonify(response)), 401
        else:
            response = {"message": 'Provide a valid auth token.'}
            return make_response(jsonify(response)), 401


class LoginView(MethodView):
    """This view handles user login action."""

    def post(self):
        """Login a user
        ---
        tags:
            - "auth"
        parameters:
          - in: "body"
            name: "body"
            description: "password, email"
            required: true
            schema:
             type: "object"
             required:
             - "password"
             - "email"
             properties:
              password:
               type: "string"
              email:
               type: "string"
        responses:
            200:
                description: "Successfully logged in"
            401:
                description: "Invalid email or password, Please try again"
            500:
                description: "Failed to log in, Something went wrong"
            """

        try:
            email = User.verify_username(request.data['email'])
            password = User.verify_password(request.data['password'])
            # Get the user model from DB by email
            user = User.query.filter_by(email=email).first()

            # Try to authenticate the found user using their password
            if user and user.password_is_valid(password):

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


class PasswordChangeView(MethodView):
    def post(self):
        """Change password of an existing user
        ---
        tags:
            - "auth"
        parameters:
          - in: "body"
            name: "body"
            description: "password, re-password"
            required: true
            schema:
             type: "object"
             required:
             - "password"
             - "repassword"
             properties:
              password:
               type: "string"
              repassword:
               type: "string"
        responses:
            200:
                description: "Successfully changed password"
            400:
                description: "Failed to change password, Invalid data supplied"
            404:
                description: "User doesn't exist"
            500:
                description: "Failed to change password, Something went wrong"
            """
        # get access token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            access_token = auth_header.split(" ")[1]
        else:
            access_token = ''
        if access_token:        
           
            try:
                repassword = User.verify_password(request.data['repassword'])
                password = User.verify_password(request.data['password'])
                if not repassword == password:
                    return {"message": 'Passwords did not match'}, 400

            except ValueError as e:
                return {"message": str(e)}, 400
            except TypeError as e:
                return {"message": str(e)}, 400
            except Exception as e:
                return {"message": str(e)}, 500
            
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                try:
                    # lets check if the user exists
                    user = User.query.filter_by(id=user_id).first()
                    if user:
                        # Grab password and save it to the database
                        user.password = user.hash_password(password)
                        user.save()

                        # Return success response to the requestor
                        response = {
                            'message': 'Successfully changed password'
                        }
                        return make_response(jsonify(response)), 200

                    else:
                        # This handles a case where user doesnt exists
                        # Return am message telling them it doesnt exist
                        return {"message": 'User does not exist. Please register'}, 404

                except Exception as e:
                    # Return to requestor a message with the error that occured
                    return {"message": str(e)}, 500

        return {"message": 'Authorization is required to access this resource'}, 401

# Lets make our rauth views callable
registration_view = RegistrationView.as_view('registration_view')
login_view = LoginView.as_view('login_view')
logout_view = LogoutView.as_view('logout_view')
password_reset_view = PasswordResetView.as_view('password_reset_view')
password_change_view = PasswordChangeView.as_view('password_change_view')

# Add the rule for the registration end point  /auth/register
# Then we can add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/v1/auth/register', view_func=registration_view, methods=['POST'])

# Define the rule for the login endpoint  /auth/login
# And then we add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/v1/auth/login', view_func=login_view, methods=['POST'])

# Define the rule for the logout endpoint  /auth/logout
# And then we add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/v1/auth/logout', view_func=logout_view, methods=['POST'])

# Define the rule for the password reset endpoint  /auth/reset-password
# And then we add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/v1/auth/reset-password',
    view_func=password_reset_view,
    methods=['POST', 'GET'])

# Define the rule for the password change  /auth/change-password
# And then we add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/v1/auth/change-password',
    view_func=password_change_view,
    methods=['POST'])