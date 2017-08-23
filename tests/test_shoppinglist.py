"""This file contains some test cases for
manipulation of shopping lists and items within them
"""
import json
from unittest import TestCase

from app import create_app, db


class ShoppingListTests(TestCase):
    """This class represents the shopping list test scenarios"""

    def setUp(self):
        """Initialise useful variables"""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.shoppinglist = {'name': 'Back to School shopping'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def register_user(self, email="user@test.com", password="test1234"):
        """This method registers a new user for testing puporses"""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/register', data=user_data)

    def login_user(self, email="user@test.com", password="test1234"):
        """This method logs in user"""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/login', data=user_data)

    def test_shoppinglist_creation(self):
        """Test API can create a shoppinglist using POST"""
        self.register_user()
        login_response = self.login_user()
        access_token = json.loads(login_response.data.decode())['access_token']

        # Create a shoppinglist by making a POST request
        result = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglist)

        # Check that server status is 201 i.e resource created
        self.assertEqual(result.status_code, 201)
        # Check that item we tried to create is in response
        self.assertIn('Back to School shopping', str(result.data))

    def test_api_can_get_all_shoppinglists(self):
        """Test API can get a shoppinglist uisng GET."""
        self.register_user()
        login_response = self.login_user()
        access_token = json.loads(login_response.data.decode())['access_token']

        # Create a shoppinglist
        res = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglist)
        self.assertEqual(res.status_code, 201)

        # Get all the shoppinglist that belong to the test user
        res = self.client().get(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
        )

        # Check that server returned status code 200 i.e OK
        self.assertEqual(res.status_code, 200)

        # Check that the list previously created is returned
        self.assertIn('Back to School shopping', str(res.data))

    def test_api_can_get_shoppinglist_by_id(self):
        """Test API can get a single shoppinglist by using it's id."""
        self.register_user()
        login_response = self.login_user()
        access_token = json.loads(login_response.data.decode())['access_token']

        # We create a test shopping list
        new_list_response = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglist)

        # Lets check if the shopping list is created
        self.assertEqual(new_list_response.status_code, 201)

        # Convert the data returned to JSON
        results = json.loads(new_list_response.data.decode())

        # Requests the server for the shopping list by ID
        get_list_by_id_reponse = self.client().get(
            '/shoppinglists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))

        # Check that the shoppinglist with ID is returned
        self.assertEqual(get_list_by_id_reponse.status_code, 200)
        self.assertIn('Back to School shopping',
                      str(get_list_by_id_reponse.data))

    def test_shoppinglist_can_be_edited(self):
        """Test API can edit an existing shoppinglist with PUT"""
        self.register_user()
        login_response = self.login_user()
        access_token = json.loads(login_response.data.decode())['access_token']

        # Lets create a shoppinglist using POST
        new_list_response = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Christmas Shopping'})
        # Make sure the list is created well
        self.assertEqual(new_list_response.status_code, 201)

        # Turn the response into JSON
        results = json.loads(new_list_response.data.decode())

        # Now Edit the created list using PUT
        edited_list_response = self.client().put(
            '/shoppinglists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "Christmas Shopping for the kids"
            })
        # Check that the server returned OK
        self.assertEqual(edited_list_response.status_code, 200)

        # Finally, we get the edited shoppinglist to see if it changed.
        edited_list_response = self.client().get(
            '/shoppinglists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('for the kids', str(edited_list_response.data))

    def test_shoppinglist_deletion(self):
        """Test that API can delete an existing shoppinglist DELETE"""
        self.register_user()
        login_response = self.login_user()
        access_token = json.loads(login_response.data.decode())['access_token']

        # Lets create a shopping list
        new_list_response = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Favourite books'})

        # Confirm that the server created the resource
        self.assertEqual(new_list_response.status_code, 201)

        # Get the shoppinglist in json
        results = json.loads(new_list_response.data.decode())

        # Delete the shoppinglist we just created above
        delete_response = self.client().delete(
            '/shoppinglists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),)
        self.assertEqual(delete_response.status_code, 200)

        # Now lets try to retrieve the entry we deleted
        response = self.client().get(
            '/shoppinglists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))

        # Check that the server could not find the resource
        self.assertEqual(response.status_code, 404)

    def test_shoppinglist_item_creation(self):
        """Test API can add items to a shopping list"""
        self.register_user()
        login_response = self.login_user()
        access_token = json.loads(login_response.data.decode())['access_token']

        # Lets first create a shopping list
        new_list_response = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Shoes and Bags'})

        # Make sure the server succesfully created resource
        self.assertEqual(new_list_response.status_code, 201)

        # Lets load the response to JSON format
        results = json.loads(new_list_response.data.decode())

        # Now lets add an item to the shoppinglist we just created
        add_item_response = self.client().post(
            '/shoppinglists/{}/items'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token), data={
                'name': 'Milk'})

        # Lets check that the server managed to create resource
        self.assertEqual(add_item_response.status_code, 201)

    def test_shoppinglist_item_edited(self):
        """Test that API can edit items to list"""
        self.register_user()
        login_response = self.login_user()
        access_token = json.loads(login_response.data.decode())['access_token']

        # Lets create a new shopping list
        new_list_response = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Shoes and Bags'})
        self.assertEqual(new_list_response.status_code, 201)

        # Get the shoppinglist in json
        results = json.loads(new_list_response.data.decode())

        # Add item to the shoppinglist we just created
        add_item_response = self.client().post(
            '/shoppinglists/{}/items'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token), data={
                'name': 'Milk'})

        # Make sure server says item was added
        self.assertEqual(add_item_response.status_code, 201)

        # Get Turn the reponse into JSON format
        results = json.loads(add_item_response.data.decode())

        # Now Lets edit the, we edit the list item
        edit_item_response = self.client().put(
            '/shoppinglists/{}/items/{}'.format(
                results['shoppinglist_id'], results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "whole milk"
            })

        # Check if the edits are reflected in the response
        self.assertIn('whole', str(edit_item_response.data))

    def test_shoppinglist_item_deletion(self):
        """Test API can add items to list"""
        self.register_user()
        login_response = self.login_user()
        access_token = json.loads(login_response.data.decode())['access_token']

        # Lets create a shopping list for this test
        new_list_response = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Shoes and Bags'})
        self.assertEqual(new_list_response.status_code, 201)

        # Turn the response to JSON format
        results = json.loads(new_list_response.data.decode())

        # Add item to the shoppinglist we just created
        add_item_response = self.client().post(
            '/shoppinglists/{}/items'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token), data={
                'name': 'Milk'})

        # Lets first make sure the item was created before we delete
        self.assertEqual(add_item_response.status_code, 201)

        # COnvert  the response to JSON
        results = json.loads(add_item_response.data.decode())

        # Now we can delete the item from the shoppinglist we just created
        delete_item_response = self.client().delete(
            '/shoppinglists/{}/items/{}'.format(
                results['shoppinglist_id'], results['id']),
            headers=dict(Authorization="Bearer " + access_token),)
        self.assertEqual(delete_item_response.status_code, 200)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
