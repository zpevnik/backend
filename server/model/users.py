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

    def create_user(self, userid, name, active):
        """Create new user and insert him into database.

        Args:
          data (dict): User data dictionary containing id, name and isActive

        Returns:
          User: Instance of the new user.
        """
        user = User({
            '_id': userid,
            'name': name,
            'active': active,
            'created': datetime.utcnow(),
            'last_login': datetime.utcnow(),
            'editor': False,
            'token': None
        })
        self._collection.insert_one(user.serialize())

        return user

    def save(self, user):
        self._collection.update_one({'_id': user.get_id()}, {'$set': user.serialize(update=True)})

    def find(self, user_id):
        doc = self._collection.find_one(user_id)
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
      _last_login (int) UTC timestamp
      _name (str) Name in the skautis
      _active (bool) True if user's account is active
      _token (str): Unique token for current skautis communication
      _editor (bool): True if user is an editor
    """

    def __init__(self, user):
        self._id = user['_id']
        self._created = user['created']
        self._last_login = user['last_login']
        self._editor = user['editor']
        self._name = user['name']
        self._active = user['active']
        self._token = user['token']

    def serialize(self, update=False):
        user = {
            'name': self._name,
            'active': self._active,
            'last_login': self._last_login,
            'editor': self._editor,
            'token': self._token
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
            'last_login': self._last_login.isoformat(),
            'editor': self._editor,
            'active': self._active
        }

    def is_authenticated(self):
        return self._token is not None

    def is_anonymous(self):
        return False

    def is_editor(self):
        return self._editor

    def is_active(self):
        return self._active

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_created(self):
        return self._created

    def get_last_login(self):
        return self._last_login

    def get_token(self):
        return self._token

    def set_token(self, token):
        self._token = token

    def __repr__(self):
        return '<{} id={} name={}>'.format(self.__class__.__name__, self._id, self._name)
