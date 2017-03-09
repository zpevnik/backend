# -*- coding: UTF-8 -*-

from flask import g
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from server.util import generate_random_uuid, uuid_from_str, uuid_to_str


class Users(object):
    """Collection for managing CRUD operation in database for users

    Args:
      model (server.model.Model): Reference to model
      db (pymongo.MongoClient): Reference to database

    Attributes:
      _model (server.model.Model): Reference to model
      _db: Reference to database
      _collection: Reference to collection in database for this class
    """

    COLLECTION_NAME = 'users'

    def __init__(self, model, db):
        self._model = model
        self._db = db
        self._collection = db[self.COLLECTION_NAME]

    def create_user(self, email, password, first_name, last_name):
        """Create new user and insert it into database.

        Args:
          email (str): User's login email.
          password (str): User's secret password.

        Returns:
          Song: Instance of the new user.
        """

        index = 1
        while True:
            short_name = generate_short_id_from_name('%s %s' % (first_name, last_name))
            if index != 1:
                short_name = '%s-%d' % (short_name, index)

            user = self.find_by_short_name(short_name)
            index += 1

            if user is None:
                break

        user = User({
            '_id': generate_random_uuid(),
            'shortName': short_name,
            'created': datetime.utcnow(),
            'email': email,
            'password': generate_password_hash(password),
            'first_name': first_name,
            'last_name': last_name,
            'authenticated': True,
            'active': True,
            'accounts': [],
            'activeAccount': None
        })
        self._collection.insert(user.serialize())

        return user

    def save(self, user):
        self._collection.update(
            {'_id': uuid_from_str(user.get_id())},
            {'$set': user.serialize(update=True)}
        )

    def find_by_id(self, userId):
        doc = self._collection.find_one(uuid_from_str(userId))

        if not doc:
            return None

        return User(doc)

    def find_by_email(self, email):
        doc = self._collection.find_one({'email': email})

        if not doc:
            return None

        return User(doc)

    def find_by_short_name(self, short_name):
        doc = self._collection.find_one({
            'shortName': short_name
        })

        if not doc:
            return None

        return User(doc)


class User(object):
    """Class for user abstraction

    Args:
      user (dict) User dictionary

    Attributes:
      _id (str) UUID
      _created (int) UTC timestamp
      _short_name (str) Unique human readable id
      _email (str) Email adress of user
      _password (str) Hashed string with salt
      _first_name (str) First name of user
      _last_name (str) Last name of user
      _authenticated (bool) True, if user confirmed registration
      _active (bool) True, if is user's account active
      _accounts (list of str) List of accounts ids
      _activeAccount(str) User's actual active account
    """

    def __init__(self, user):
        self._id = uuid_to_str(user['_id'])
        self._created = user['created']
        self._short_name = user['shortName']
        self._email = user['email']
        self._password = user['password']
        self._first_name = user['first_name']
        self._last_name = user['last_name']
        self._authenticated = user['authenticated']
        self._active = user['active']
        self._accounts = []
        self._active_account = uuid_to_str(user['activeAccount'])

        self._active_player = None

        for account_uuid in user['accounts']:
            self._accounts.append(uuid_to_str(account_uuid))

    def serialize(self, update=False):
        accounts = []
        for account in self._accounts:
            accounts.append(uuid_from_str(account))

        user = {
            'shortName': self._short_name,
            'email': self._email,
            'password': self._password,
            'first_name': self._first_name,
            'last_name': self._last_name,
            'authenticated': self._authenticated,
            'active': self._active,
            'accounts': accounts,
            'activeAccount': uuid_from_str(self._active_account)
        }

        if not update:
            user['_id'] = uuid_from_str(self._id)
            user['created'] = self._created

        return user

    def get_serialized_data(self):
        transactions = []
        transactions_doc = g.model.transactions.find_by_account_id(self._active_account)
        for transaction in transactions_doc:
            transactions.append(transaction.get_serialized_data())

        return {
            'id': self._id,
            'created': self._created.isoformat(),
            'shortName': self._short_name,
            'email': self._email,
            'firstName': self._first_name,
            'lastName': self._last_name,
            'name': '%s %s' % (self._first_name, self._last_name),
            'accounts': self._accounts,
            'activeAccount': self._active_account,
            'transactions': transactions
        }

    def authenticate(self):
        self._authenticated = True

    def is_authenticated(self):
        return self._authenticated

    def is_active(self):
        return self._active

    def is_anonymous(self):
        return False

    def get_id(self):
        return self._id

    def get_first_name(self):
        return self._first_name

    def get_last_name(self):
        return self._last_name

    def get_name(self):
        return '%s %s' % (self._first_name, self._last_name)

    def get_email(self):
        return self._email

    def get_created(self):
        return self._created

    def get_accounts(self):
        return self._accounts

    def add_account(self, id):
        self._accounts.append(id)

    def get_active_account(self):
        return self._active_account

    def set_active_account(self, account):
        self._active_account = account

    def get_active_player(self):
        if self._active_player is None:
            self._active_player = g.model.players.find_one(account=self._active_account).get_id()
        return self._active_player

    def check_password(self, password):
        return check_password_hash(self._password, password)

    def get_selected_team(self):
        account = g.model.accounts.find_by_id(self._active_account)
        return account.get_team()

    def __repr__(self):
        return '<%r id=%r email=%r first_name=%r last_name=%r>' % (self.__class__.__name__, self._id, self._email, self._first_name, self._last_name)
