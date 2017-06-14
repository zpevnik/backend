# -*- coding: UTF-8 -*-

from datetime import datetime


class Users(object):
    """Collection for managing CRUD operation in database for user

    Args:
      model (taskino_server.model.Model): Reference to model
      db (pymongo.MongoClient): Reference to database

    Attributes:
      _model (taskino_server.model.Model): Reference to model
      _db: Reference to database
      _collection: Reference to collection in database for this class
    """

    COLLECTION_NAME = 'users'

    def __init__(self, model, db):
        self._model = model
        self._db = db
        self._collection = db[self.COLLECTION_NAME]

    def create_user(self, userid, name, active, unit):
        """Create new user and insert him into database.

        Args:
          data (dict): User data dictionary containing id, name, isActive and unit

        Returns:
          User: Instance of the new user.
        """
        user = User({
            '_id': userid,
            'name': name,
            'active': active,
            'unit': unit,
            'created': datetime.utcnow(),
            'lastLogin': datetime.utcnow(),
            'token': None
        })
        self._collection.insert(user.serialize())

        return user

    def save(self, user):
        self._collection.update(
            {'_id': user.get_id()},
            {'$set': user.serialize(update=True)}
        )

    def find(self, userid):
        doc = self._collection.find_one(userid)
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
      _lastLogin (int) UTC timestamp
      _name (str) Name in the skautis
      _active (bool) True, if is user's account active
      _token (str): Unique token for current skautis communication
      _unit (str): Unique identifier of scout unit
    """

    def __init__(self, user):
        self._id = user['_id']
        self._created = user['created']
        self._lastLogin = user['lastLogin']
        self._name = user['name']
        self._active = user['active']
        self._token = user['token']
        self._unit = user['unit']

    def serialize(self, update=False):
        user = {
            'name': self._name,
            'active': self._active,
            'lastLogin': self._lastLogin,
            'token': self._token,
            'unit': self._unit
        }

        if not update:
            user['_id'] = self._id
            user['created'] = self._created

        return user

    def get_serialized_data(self):
        return {
            'id': self._id,
            'name': self._name,
            'created': self._created.isoformat(),
            'lastLogin': self._lastLogin.isoformat(),
            'active': self._active,
            'unit': self._unit
        }

    def is_authenticated(self):
        return self._token is not None

    def is_anonymous(self):
        return False

    def is_active(self):
        return self._active

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_created(self):
        return self._created

    def get_lastLogin(self):
        return self._lastLogin

    def get_token(self):
        return self._token

    def get_unit(self):
        return self._unit

    def set_token(self, token):
        self._token = token

    def __repr__(self):
        return '<{} id={} name={}>'.format(self.__class__.__name__, self._id, self._name)
