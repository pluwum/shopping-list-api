from flask import request
from functools import wraps
from app.models import User


def check_logged_in(function):
    @wraps(function)
    def wrapper(self, *args, **kwargs):
        # Get token authentication information from header
        auth_header = request.headers.get('Authorization')
        message = "Not permited because Authorization header not " \
            "provided with this request!"
        if auth_header is not None:
            # Split Bearer and token then grab the token
            access_token = auth_header.split(" ")[1]

            if access_token:
                # Decode user info from jwt hashed token
                user_id = User.decode_token(access_token)

                # Check if user is user is authenticated
                if not isinstance(user_id, str):
                    return function(self, user_id, *args, **kwargs)
                else:
                    message = user_id
        return {"message": message}, 401

    return wrapper