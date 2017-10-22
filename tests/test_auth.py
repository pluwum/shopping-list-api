"""This file carries test cases for the shopping list API's Authentication
 features
"""
import json
import time
from unittest import TestCase
from app.models import BlacklistToken
from app import create_app, db


class AuthTestCase(TestCase):
    """Test cases for the API authentication"""

    def setUp(self):
        """Set up some helpful variables."""
        self.app = create_app(config_name="testing")

        # Initialize the test client
        self.client = self.app.test_client

        # Initialise a test user's data for later
        self.user_data = {
            'email': 'test@example.com',
            'password': 'test_password'
        }

        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_user_registration(self):
        """Test that user can register successfully"""
        register_user_response = self.client().post(
            '/auth/register', data=self.user_data)

        # Convert respponse to JSON format
        result = json.loads(register_user_response.data.decode())

        # Assert that the request contains a success message
        self.assertEqual(result['message'],
                         "You registered successfully. Please log in.")
        # Check that server created resource successfully
        self.assertEqual(register_user_response.status_code, 201)

    def test_that_user_already_registered(self):
        """Test that a user cannot be registered twice."""
        # Lets create a new user and check that they are created
        register_firsttime_user_response = self.client().post(
            '/auth/register', data=self.user_data)
        self.assertEqual(register_firsttime_user_response.status_code, 201)

        # Lets try creating the user a second time
        register_secondtime_user_response = self.client().post(
            '/auth/register', data=self.user_data)
        self.assertEqual(register_secondtime_user_response.status_code, 202)

        # Get the results returned in JSON format
        result = json.loads(register_secondtime_user_response.data.decode())
        self.assertEqual(result['message'],
                         "User already exists. Please login.")

    def test_user_can_login(self):
        """Test registered user can login."""
        register_user_response = self.client().post(
            '/auth/register', data=self.user_data)
        self.assertEqual(register_user_response.status_code, 201)

        login_response = self.client().post('/auth/login', data=self.user_data)

        # get the results in json format
        result = json.loads(login_response.data.decode())

        # Test that the response contains success message
        self.assertEqual(result['message'], "You logged in successfully.")

        # Assert that the status code is equal to 200-OK
        self.assertEqual(login_response.status_code, 200)

        # Check that an access token is generated for the session
        self.assertTrue(result['access_token'])

    def test_non_registered_user_login(self):
        """Test non registered users cannot login"""
        # Define test data for an unregistered user
        not_a_user = {'email': 'not_a_user@example.com', 'password': 'nope'}
        # Now lets try loggin in as above user
        login_response = self.client().post('/auth/login', data=not_a_user)
        # Get the result as JSON format
        result = json.loads(login_response.data.decode())

        # assert that this response must contain an error message
        # and an error status code 401(Unauthorized)
        self.assertEqual(login_response.status_code, 401)
        self.assertEqual(result['message'],
                         "Invalid email or password, Please try again")

    def test_user_can_logout(self):
        """Test logged in user can log out"""
        register_user_response = self.client().post(
            '/auth/register', data=self.user_data)
        self.assertEqual(register_user_response.status_code, 201)

        # user login
        login_response = self.client().post('/auth/login', data=self.user_data)

        # get the results in json format
        result = json.loads(login_response.data.decode())

        # Test that the response contains success message
        self.assertEqual(result['message'], "You logged in successfully.")

        # Assert that the status code is equal to 200-OK
        self.assertEqual(login_response.status_code, 200)

        # Check that an access token is generated for the session
        self.assertTrue(result['access_token'])

        # valid token logout
        logout_response = self.client().post(
            '/auth/logout',
            headers=dict(Authorization='Bearer ' + result['access_token']))

        result = json.loads(logout_response.data.decode())

        self.assertTrue(result['message'] == 'Successfully logged out.')
        self.assertEqual(logout_response.status_code, 200)

    def test_valid_blacklisted_token_logout(self):
        """ Test for logout after a valid token gets blacklisted """

        with self.app.app_context():
            register_user_response = self.client().post(
                '/auth/register', data=self.user_data)

            self.assertEqual(register_user_response.status_code, 201)

            # user login
            login_response = self.client().post(
                '/auth/login', data=self.user_data)

            # get the results in json format
            result = json.loads(login_response.data.decode())

            # blacklist a valid token
            blacklist_token = BlacklistToken(token=result['access_token'])
            blacklist_token.save()

            # blacklisted valid token logout
            logout_response = self.client().post(
                '/auth/logout',
                headers=dict(Authorization='Bearer ' + result['access_token']))

            result = json.loads(logout_response.data.decode())

            self.assertTrue(
                result['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(logout_response.status_code, 401)
