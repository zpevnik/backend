import datetime

from bson import ObjectId
from flask import g

from server.util import validators
from server.util import SongbookTemplate

from server.constants import OPTIONS
from server.constants import DEFAULTS
from server.constants import PERMISSION


class Songbooks(object):
    """Collection for managing CRUD operation in database for songbooks.

    Args:
      model (server.model.Model): Reference to model.
      db (pymongo.MongoClient): Reference to database.

    Attributes:
      _model (server.model.Model): Reference to model.
      _db: Reference to database.
      _collection: Reference to collection in database for this class.
    """

    COLLECTION_NAME = 'songbooks'

    def __init__(self, model, db):
        self._model = model
        self._db = db
        self._collection = db[self.COLLECTION_NAME]

    def create_songbook(self, data):
        """Create new songbook and insert it into database.

        Args:
          data (dict): Songbook data containing 'title', 'owner' dictionary key.

        Returns:
          Songbook: Instance of the new songbook.
        """
        songbook = Songbook({
            '_id': ObjectId(),
            'title': data['title'],
            'owner': data['owner'],
            'options': data['options'] if 'options' in data else DEFAULTS.SONGBOOK_OPTIONS,
            'songs': data['songs'] if 'songs' in data else [],
            'cached_file': None,
            'cache_expiration': None,
        }) # yapf: disable
        self._collection.insert_one(songbook.serialize())

        return songbook

    def save(self, songbook):
        """Save songbook into the database.

        Args:
          songbook (Songbook): Instance of the songbook.
        """
        self._collection.update_one(
            {
                '_id': songbook._id
            }, {
                '$set': songbook.serialize(update=True)
            })

    def delete(self, songbook):
        """Delete songbook from the database.

        Args:
          songbook (Songbook): Instance of the songbook.
        """
        self._collection.delete_one({'_id': songbook._id})

    def find(self):
        """Find all songbooks in the database."""
        doc = self._collection.find({})

        songbooks = []
        for songbook in doc:
            songbooks.append(Songbook(songbook))

        return songbooks

    def find_filtered(self, query, user_id):
        """Find songbooks from the database based on query and permissions.

        Args:
          query (str): Query string.
          user_id (str): user Id string.

        All returned songbooks are accessible by this user. If the query string
        is empty, every accessible songbook is returned.

        Returns:
          list: List of Songbook instances satisfying the query.
        """
        if query is None or query == "":
            doc = self._collection.find({'owner': user_id})
        else:
            doc = self._collection.find({'owner': user_id, '$text': {'$search': query}},
                                        {'score': {'$meta': 'textScore'}}) \
                                  .sort([('score', {'$meta': 'textScore'})])

        songbooks = []
        for songbook in doc:
            songbooks.append(Songbook(songbook))
        return songbooks

    def find_one(self, songbook_id=None, title=None):
        """Find one songbook based on given arguments.

        Args:
          songbook_id (str, optional): Songbook ObjectId string.
          title (str, optional): Title of the songbook.

        Returns:
          Songbook: One Songbook or None if it does not exist.
        """
        query = {}
        if songbook_id is not None:
            query['_id'] = ObjectId(songbook_id)
        if title is not None:
            query['title'] = title

        doc = self._collection.find_one(query)
        if not doc:
            return None

        return Songbook(doc)


class Songbook(object):
    """Class for songbook abstraction.

    Args:
      songbook (dict): Songbook dictionary.

    Attributes:
      _id (str): Songbook ObjectId.
      _title (str): Songbook title.
      _songs (dict): Songs contained in this songbook.
      _owner (str): User Id
      _cached_file (str): Filename of cached songbook
      _cache_expiration (str): Timestamp of the cache expiration creation.
    """

    def __init__(self, songbook):
        self._id = songbook['_id']
        self._title = songbook['title']
        self._songs = songbook['songs']
        self._owner = songbook['owner']
        self._options = songbook['options']

        self._cached_file = songbook['cached_file']
        self._cache_expiration = songbook['cache_expiration']

    def serialize(self, update=False):
        """Serialize songbook data for database operations.

        Args:
          update (bool, optional): Determines whether method returns only
            update attributes or data for new database entry.
        """
        songbook = {
            'title': self._title,
            'songs': self._songs,
            'owner': self._owner,
            'options': self._options,
            'cached_file': self._cached_file,
            'cache_expiration': self._cache_expiration
        }

        if not update:
            songbook['_id'] = self._id

        return songbook

    def get_serialized_data(self):
        # map extended songs representations on songs list
        extended_data = g.model.variants.find_extended_songbook_items(self._songs)

        return {
            'id': str(self._id),
            'created': self._id.generation_time,
            'title': self._title,
            'songs': extended_data,
            'owner': self._owner,
            'options': self._options
        }

    def get_id(self):
        return str(self._id)

    def get_creation_date(self):
        return self._id.generation_time

    def get_title(self):
        return self._title

    def get_songs(self):
        return self._songs

    def get_owner(self):
        return self._owner

    def get_options(self):
        return self._options

    def is_cached(self):
        return self._cached_file is not None

    def is_cache_valid(self):
        return self._cache_expiration is not None and \
            datetime.datetime.utcnow() < self._cache_expiration

    def get_cached_file(self, extend=False):
        if extend:
            self.extend_cache()
        return self._cached_file

    def extend_cache(self):
        self._cache_expiration = datetime.datetime.utcnow() + datetime.timedelta(days=14)

    def cache_file(self, link):
        self._cached_file = link
        self._cache_expiration = datetime.datetime.utcnow() + datetime.timedelta(days=14)

        # save cached songbook into database
        g.model.songbooks.save(self)

    def invalidate_cache(self):
        self._cached_file = None
        self._cache_expiration = None

    def set_title(self, title):
        self.invalidate_cache()
        self._title = title

    def set_songs(self, songs):
        self.invalidate_cache()
        self._songs = songs

    def set_options(self, options):
        self.invalidate_cache()
        self._options = options

    def set_data(self, data):
        self.invalidate_cache()

        self._title = data['title']
        self._options = data['options']
        self._songs = data['songs']

    def get_output_template(self):
        return SongbookTemplate(self._options)

    def __repr__(self):
        return '<{!r} id={!r} title={!r}>' \
            .format(self.__class__.__name__, self._id, self._title)
