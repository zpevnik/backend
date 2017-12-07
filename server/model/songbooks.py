import datetime

from bson import ObjectId
from flask import g

from server.util import validators
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
          data (dict): Songbook data containing 'title', 'owner',
            'owner_unit', 'visibility' and 'edit_perm' dictionary key.

        Returns:
          Songbook: Instance of the new songbook.
        """
        songbook = Songbook({
            '_id': ObjectId(),
            'title': data['title'],
            'owner': data['owner'],
            'owner_unit': data['owner_unit'],
            'visibility': data['visibility'],
            'edit_perm': data['edit_perm'],
            'options': DEFAULTS.SONGBOOK_OPTIONS,
            'songs': {},
            'cached_file': None,
            'cache_expiration': None,
        })
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
        """Find all authors in the database."""
        doc = self._collection.find({})

        songbooks = []
        for songbook in doc:
            songbooks.append(Songbook(songbook))

        return songbooks

    def find_special(self, data):
        """Find songbooks from the database based on query and page the result.

        Args in dict:
          query (str): Query string.
          page (int): Result page number.
          per_page (int): Number of songbooks per search result.
          user (str): user Id string
          unit (str): Unit Id string

        If the query string is empty, whole database is returned (and paged).

        Returns:
          list: List of Songbook instances satisfying the query.
        """
        if data['query'] is None or data['query'] == "":
            doc = self._collection.find({}).skip(data['page'] * data['per_page']) \
                                  .limit(data['per_page'])
        else:
            doc = self._collection.find({'$text':{'$search': data['query']}},
                                        {'score': {'$meta': "textScore"}}) \
                                  .sort([('score', {'$meta': 'textScore'})]) \
                                  .skip(data['page'] * data['per_page']).limit(data['per_page'])
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
      _owner_unit (str): Unit Id
      _visibility (str): Songbook visibility status
      _edit_perm (str): Editing permission status
      _cached_file (str): Filename of cached songbook
      _cache_expiration (str): Timestamp of the cache expiration creation.
    """

    def __init__(self, songbook):
        self._id = songbook['_id']
        self._title = songbook['title']
        self._songs = songbook['songs']
        self._owner = songbook['owner']
        self._options = songbook['options']
        self._owner_unit = songbook['owner_unit']
        self._visibility = songbook['visibility']
        self._edit_perm = songbook['edit_perm']

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
            'owner_unit': self._owner_unit,
            'visibility': self._visibility,
            'edit_perm': self._edit_perm,
            'cached_file': self._cached_file,
            'cache_expiration': self._cache_expiration
        }

        if not update:
            songbook['_id'] = self._id

        return songbook

    def get_serialized_data(self):
        return {
            'id': str(self._id),
            'created': self._id.generation_time,
            'title': self._title,
            'songs': list(self._songs.values()),
            'owner': self._owner,
            'options': self._options,
            'owner_unit': self._owner_unit,
            'visibility': self._visibility,
            'edit_perm': self._edit_perm
        }

    def get_id(self):
        return str(self._id)

    def get_creation_date(self):
        return self._id.generation_time

    def get_songs(self):
        return self._songs

    def get_owner(self):
        return self._owner

    def get_owner_unit(self):
        return self._owner_unit

    def get_visibility(self):
        return self._visibility

    def get_edit_perm(self):
        return self._edit_perm

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

    def set_data(self, data):
        self.invalidate_cache()

        self._title = data['title'] if 'title' in data else self._title
        if 'visibility' in data:
            if data['visibility'] in PERMISSION:
                self._visibility = data['visibility']
        if 'edit_perm' in data:
            if data['edit_perm'] in PERMISSION:
                self._edit_perm = data['edit_perm']
        if 'options' in data:
            self._options = validators.songbook_options(data['options'])

    def get_position(self):
        return max((x['order'] if 'order' in x else 0) for x in self._songs.values()) + 1

    def set_song(self, song_id, data):
        self.invalidate_cache()

        if song_id not in self._songs:
            self._songs[song_id] = {'id': song_id}
            if 'order' not in data:
                self._songs[song_id]['order'] = self.get_position()
        if 'order' in data:
            self._songs[song_id]['order'] = data['order']

    def remove_song(self, song_id):
        self.invalidate_cache()
        self._songs.pop(song_id, None)

    def __repr__(self):
        return '<{!r} id={!r} title={!r}>' \
            .format(self.__class__.__name__, self._id, self._title)
