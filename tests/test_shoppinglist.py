from unittest import TestCase
import os
import json
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
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/register', data=user_data)

    def login_user(self, email="user@test.com", password="test1234"):
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/login', data=user_data)

    def test_shoppinglist_creation(self):
        """Test API can create a shoppinglist (POST request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist by making a POST request
        res = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglist)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Back to School shopping', str(res.data))

    def test_api_can_get_all_shoppinglists(self):
        """Test API can get a shoppinglist (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist by making a POST request
        res = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglist)
        self.assertEqual(res.status_code, 201)

        # get all the shoppinglist that belong to the test user by making a GET request
        res = self.client().get(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Back to School shopping', str(res.data))

    def test_api_can_get_shoppinglist_by_id(self):
        """Test API can get a single shoppinglist by using it's id."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglist)

        # assert that the shoppinglist is created
        self.assertEqual(rv.status_code, 201)
        # get the response data in json format
        results = json.loads(rv.data.decode())

        result = self.client().get(
            '/shoppinglists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        # assert that the shoppinglist is actually returned given its ID
        self.assertEqual(result.status_code, 200)
        self.assertIn('Back to School shopping', str(result.data))

    def test_shoppinglist_can_be_edited(self):
        """Test API can edit an existing shoppinglist. (PUT request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # first, we create a shoppinglist by making a POST request
        rv = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Christmas Shopping'})
        self.assertEqual(rv.status_code, 201)
        # get the json with the shoppinglist
        results = json.loads(rv.data.decode())

        # then, we edit the created shoppinglist by making a PUT request
        rv = self.client().put(
            '/shoppinglists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "Christmas Shopping for the kids"
            })
        self.assertEqual(rv.status_code, 200)

        # finally, we get the edited shoppinglist to see if it is actually edited.
        results = self.client().get(
            '/shoppinglists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('for the kids', str(results.data))

    def test_shoppinglist_deletion(self):
        """Test API can delete an existing shoppinglist. (DELETE request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Eat, pray and love'})
        self.assertEqual(rv.status_code, 201)
        # get the shoppinglist in json
        results = json.loads(rv.data.decode())

        # delete the shoppinglist we just created
        res = self.client().delete(
            '/shoppinglists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),)
        self.assertEqual(res.status_code, 200)

        # Test to see if it exists, should return a 404
        result = self.client().get(
            '/shoppinglists/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)

    def test_shoppinglist_item_creation(self):
        """Test API can add items to list"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Shoes and Bags'})
        self.assertEqual(rv.status_code, 201)
        # get the shoppinglist in json
        results = json.loads(rv.data.decode())

        # Add item to the shoppinglist we just created
        res = self.client().post(
            '/shoppinglists/{}/items'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token), data={'name': 'Milk'})

        self.assertEqual(res.status_code, 201)

    def test_shoppinglist_item_edited(self):
        """Test API can add items to list"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Shoes and Bags'})
        self.assertEqual(rv.status_code, 201)
        # get the shoppinglist in json
        results = json.loads(rv.data.decode())

        # Add item to the shoppinglist we just created
        res = self.client().post(
            '/shoppinglists/{}/items'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token), data={'name': 'Milk'})

        self.assertEqual(res.status_code, 201)
        # get the json with the shoppinglist
        results = json.loads(res.data.decode())

        # then, we edit the created shoppinglist by making a PUT request
        rv = self.client().put(
            '/shoppinglists/{}/items/{}'.format(results['shoppinglist_id'], results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "whole milk"
            })

        self.assertIn('whole', str(rv.data))

    def test_shoppinglist_item_deletion(self):
        """Test API can add items to list"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Shoes and Bags'})
        self.assertEqual(rv.status_code, 201)
        # get the shoppinglist in json
        results = json.loads(rv.data.decode())

        # Add item to the shoppinglist we just created
        res = self.client().post(
            '/shoppinglists/{}/items'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token), data={'name': 'Milk'})

        self.assertEqual(res.status_code, 201)
        # get the json with the shoppinglist
        results = json.loads(res.data.decode())

        # delete item from the shoppinglist we just created
        res = self.client().delete(
            '/shoppinglists/{}/items/{}'.format(results['shoppinglist_id'], results['id']),
            headers=dict(Authorization="Bearer " + access_token),)
        self.assertEqual(res.status_code, 200)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()