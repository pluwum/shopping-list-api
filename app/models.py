"""This file contains the classes that define the structure
of The API's database tables
"""
from datetime import datetime, timedelta

import jwt
from app import db
from app.exceptions import ValueNotFoundError
from flask_bcrypt import Bcrypt


class User(db.Model):
    """This class defines the users table """

    __tablename__ = 'users'

    # Define the columns of the users table, starting with the primary key
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    shoppinglists = db.relationship(
        'ShoppingList',
        order_by='ShoppingList.id',
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

    def hash_password(self, password):
        return Bcrypt().generate_password_hash(password).decode()

    def generate_token(self, user_id):
        """This Generates the access token"""

        try:
            # Set up a time based payload
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=525600000),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            # Create the byte string token using the payload and the SECRET key
            encoded_jwt = jwt.encode(payload, 'mys3cr3t', algorithm='HS256')
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

            # Check if token is blacklisted
            is_blacklisted_token = BlacklistToken.check_blacklist(token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'

            return payload['sub']
        except jwt.ExpiredSignatureError:
            # When the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # When the token is invalid, return an error string
            return "Invalid token. Please register or login"

    @staticmethod
    def verify_username(username):
        username = username.strip()
        
        min_length = 5
        if username is None:
            raise ValueError('Email cannot be empty or only spaces')
        if len(username) < min_length:
            raise ValueError(
                'Email cannot be less than {} '.format(min_length))
        if not isinstance(username, str):
            raise TypeError('Email must be as string')
        return username

    @staticmethod
    def verify_password(password):
        password = password.strip()
        min_length = 4
        if password is None:
            raise ValueError('Password cannot be empty or only spaces')
        if len(password) < min_length:
            raise ValueError(
                'Password cannot be less than {} characters'.format(
                    min_length))
        if not isinstance(password, str):
            raise TypeError('Password must be as string')
        return password


class ShoppingList(db.Model):
    """This class represents the shoppinglists table."""

    __tablename__ = 'shoppinglist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255), nullable=True)

    # Define auto populated columns for create and update time
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    # Define user id column for associated user
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    # Define a one-to-many relationship with items that belong
    shoppinglist_items = db.relationship(
        'ShoppingListItem',
        order_by='ShoppingListItem.id',
        cascade="all, delete-orphan")

    def __init__(self, name, user_id, description):
        """Initialize with name and user id"""
        self.name = name
        self.user_id = user_id
        self.description = description

    def save(self):
        """Save modifications or create the list model in the database"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all(user_id, page=None, per_page=None):
        """Get all lists belonging to user_id"""
        return ShoppingList.query.filter_by(user_id=user_id).paginate(
            page, per_page).items

    def delete(self):
        """Delete User model from the database"""
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_shopping_list(user_id, id):
        shoppinglist = ShoppingList.query.filter_by(
            id=id, user_id=user_id).first()

        if not shoppinglist:
            # When no shopping list is found, we throw an error
            raise ValueNotFoundError(
                'A shopping list with given ID was not found for this user')
        return shoppinglist

    def __repr__(self):
        """Lets return a printable representation of this object as
        good practice"""
        return "<Shoppinglist: {}>".format(self.name)

    @staticmethod
    def verify_name(name):
        name = name.strip()
        min_length = 2
        if name is None:
            raise ValueError('Name cannot be empty or only spaces')
        if len(name) < min_length:
            raise ValueError('Name cannot be less than {} '.format(min_length))
        if not isinstance(name, str):
            raise TypeError('Name must be as string')
        return name

    @staticmethod
    def verify_description(description):
        description = description.strip()
        if description is None:
            raise ValueError('Description cannot be empty or only spaces')
        if not isinstance(description, str):
            raise TypeError('Description must be as string')
        return description


class ShoppingListItem(db.Model):
    """This class represents the shoppinglists item table."""

    __tablename__ = 'item_shoppinglist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255), nullable=True)

    # Define a relational column to the parent shopping list
    shoppinglist_id = db.Column(db.Integer, db.ForeignKey(ShoppingList.id))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self, name, shoppinglist_id, description):
        """initialize with name"""
        self.name = name
        self.shoppinglist_id = shoppinglist_id
        self.description = description

    def save(self):
        """Save or update items in the database"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all(shoppinglist_id, page=None, per_page=None):
        """Get all lists belonging to user_id"""
        return ShoppingListItem.query.filter_by(
            shoppinglist_id=shoppinglist_id).paginate(page, per_page).items

    @staticmethod
    def get_shopping_list_item(id):
        shoppinglist_item = ShoppingListItem.query.filter_by(id=id).first()

        if not shoppinglist_item:
            # When no shopping list item is found, we throw an error
            raise ValueNotFoundError(
                'A shopping list Item with given ID was not found for this \
                user'
            )
        return shoppinglist_item

    def delete(self):
        """Deletes shopping list item from the database"""
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def verify_name(name):
        name = name.strip()
        min_length = 2
        if name is None:
            raise ValueError('name cannot be empty or only spaces')
        if len(name) < min_length:
            raise ValueError('name cannot be less than {} '.format(min_length))
        if not isinstance(name, str):
            raise TypeError('name must be as string')
        return name

    @staticmethod
    def verify_description(description):
        description = description.strip()
        if description is None:
            raise ValueError('Description cannot be empty or only spaces')
        if not isinstance(description, str):
            raise TypeError('Description must be as string')
        return description

    def __repr__(self):
        """ Prints out a representation of the item object"""
        return "<Shoppinglist Item: {}>".format(self.name)


class BlacklistToken(db.Model):
    """
    This represents the table that stores tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    def save(self):
        """Save or update items in the database"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        result = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if result:
            return True
        else:
            return False
