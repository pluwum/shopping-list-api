"""This file contains the classes that define the structure
of The API's database tables
"""
from datetime import datetime, timedelta

import jwt
from app import db
from flask_bcrypt import Bcrypt


class User(db.Model):
    """This class defines the users table """

    __tablename__ = 'users'

    # Define the columns of the users table, starting with the primary key
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    shoppinglists = db.relationship(
        'ShoppingList', order_by='ShoppingList.id',
        cascade="all, delete-orphan")

    def __init__(self, email, password):
        """Initialize the user with an email and a password."""
        self.email = email
        self.password = Bcrypt().generate_password_hash(password).decode()

    def password_is_valid(self, password):
        """Validates user password by comparing hash and the user's password
        """
        return Bcrypt().check_password_hash(self.password, password)

    def save(self):
        """This Creates or updates the user in Database
        """
        db.session.add(self)
        db.session.commit()

    def generate_token(self, user_id):
        """This Generates the access token"""

        try:
            # Set up a time based payload
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=3600),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            # Create the byte string token using the payload and the SECRET key
            encoded_jwt = jwt.encode(
                payload,
                'mys3cr3t',
                algorithm='HS256'
            )
            return encoded_jwt

        except Exception as e:
            # Return an error in string format if an exception occurs
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decodes the access token from the Authorization header."""
        try:
            # Lets try to decode the token using our SECRET variable
            payload = jwt.decode(token, 'mys3cr3t')
            return payload['sub']
        except jwt.ExpiredSignatureError:
            # When the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # When the token is invalid, return an error string
            return "Invalid token. Please register or login"


class ShoppingList(db.Model):
    """This class represents the shoppinglists table."""

    __tablename__ = 'shoppinglist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    # Define auto populated columns for create and update time
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    # Define user id column for associated user
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    # Define a one-to-many relationship with items that belong
    shoppinglist_items = db.relationship(
        'ShoppingListItem', order_by='ShoppingListItem.id',
        cascade="all, delete-orphan")

    def __init__(self, name, user_id):
        """Initialize with name and user id"""
        self.name = name
        self.user_id = user_id

    def save(self):
        """Save modifications or create the list model in the database"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all(user_id):
        """Get all lists belonging to user_id"""
        return ShoppingList.query.filter_by(user_id=user_id)

    def delete(self):
        """Delete User model from the database"""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        """Lets return a printable representation of this object as
        good practice"""
        return "<Shoppinglist: {}>".format(self.name)


class ShoppingListItem(db.Model):
    """This class represents the shoppinglists item table."""

    __tablename__ = 'item_shoppinglist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    # Define a relational column to the parent shopping list
    shoppinglist_id = db.Column(db.Integer, db.ForeignKey(ShoppingList.id))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self, name, shoppinglist_id):
        """initialize with name"""
        self.name = name
        self.shoppinglist_id = shoppinglist_id

    def save(self):
        """Save or update items in the database"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all(shoppinglist_id):
        """Returns all items in the shopping list specified"""
        return ShoppingList.query.filter_by(shoppinglist_id=shoppinglist_id)

    def delete(self):
        """Deletes shopping list item from the database"""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        """ Prints out a representation of the item object"""
        return "<Shoppinglist Item: {}>".format(self.name)
