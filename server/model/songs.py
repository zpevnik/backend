import pymongo

from bson import ObjectId
from flask import g

from server.util import AppException
from server.util import translate_to_tex

from server.constants import EVENTS
from server.constants import EXCODES
from server.constants import STRINGS
from server.constants import ORDERING
from server.constants import PERMISSION


class Songs(object):
    """Collection for managing CRUD operation in database for songs.

    Args:
      model (server.model.Model): Reference to model.
      db (pymongo.MongoClient): Reference to database.

    Attributes:
      _model (server.model.Model): Reference to model.
      _db: Reference to database.
      _collection: Reference to collection in database for this class.
    """

    COLLECTION_NAME = 'songs'

    def __init__(self, model, db):
        self._model = model
        self._db = db
        self._collection = db[self.COLLECTION_NAME]

    def create_song(self, data):
        """Create new song and insert it into database.

        Args:
          data (dict): Song data dictionary containing 'owner', 'title', 'text',
            'description', 'authors', 'variants', 'interpreters' and
            'visibility' dictionary key.

        Returns:
          Song: Instance of the new song.
        """
        song = Song({
            '_id': ObjectId(),
            'title': data['title'],
            'owner': data['owner'],
            'text': data['text'] if 'text' in data else '',
            'description': data['description'] if 'description' in data else '',
            'authors': data['authors'] if 'authors' in data else {
                'lyrics': [],
                'music': []
            },
            'interpreters': data['interpreters'] if 'interpreters' in data else [],
            'visibility': data['visibility'],
            'approved': False,
            'export_cache': None
        })
        self._collection.insert_one(song.serialize())

        return song

    def save(self, song):
        """Save song into the database.

        Args:
          song (Song): Instance of the song.
        """
        self._collection.update_one({'_id': song._id}, {'$set': song.serialize(update=True)})

    def delete(self, song):
        """Delete song from the database.

        Args:
          song (Song): Instance of the song.
        """
        self._collection.delete_one({'_id': song._id})

    def find(self):
        """Find all songs in the database."""
        doc = self._collection.find({})

        songs = []
        for song in doc:
            songs.append(Song(song))

        return songs

    def find_filtered(self, query, order, user_id):
        """Find songs from the database based on query and permissions.

        Args:
          query (str): Query string.
          user_id (str): user Id string.

        All returned songs are accessible by this user. If the query string
        is empty, every accessible song is returned.

        Returns:
          list: List of Song instances satisfying the query.
        """
        if query is None or query == "":
            doc = self._collection.find({'$or': [{'owner': user_id},
                                                 {'visibility': {"$gte": PERMISSION.PUBLIC}},
                                                ]}) # yapf: disable
        else:
            doc = self._collection.find({'$or': [{'owner': user_id},
                                                 {'visibility': {"$gte": PERMISSION.PUBLIC}},
                                                ], '$text': {'$search': query}},
                                        {'score': {'$meta': 'textScore'}}) \
                                  .sort([('score', {'$meta': 'textScore'})]) # yapf: disable

        # sort result based on order by value
        if order is not None:
            if order == ORDERING.TITLE:
                doc.sort("title", pymongo.ASCENDING)
            elif order == ORDERING.TITLE_DESC:
                doc.sort("title", pymongo.DESCENDING)

        songs = []
        for song in doc:
            songs.append(Song(song))
        return songs

    def find_one(self, song_id=None, title=None):
        """Find one song based on given arguments.

        Args:
          song_id (str, optional): Song ObjectId string.
          title (str, optional): Title of the song.

        Returns:
          Author: One Song or None if it does not exist.
        """
        query = {}
        if song_id is not None:
            query['_id'] = ObjectId(song_id)
        if title is not None:
            query['title'] = title

        doc = self._collection.find_one(query)
        if not doc:
            return None

        return Song(doc)

    def find_multiple(self, song_ids=[]):
        """Find multiple songs based on given arguments.

        Args:
          song_ids (list, required): Array of Song ObjectId strings.

        Returns:
          Author: Multiple Songs or None if non of them does not exist.
        """
        songs = []
        query_array = []

        for song_id in song_ids:
            query_array.append(ObjectId(song_id['id']))

        doc = self._collection.find({'_id': {"$in": query_array}})
        for song in doc:
            songs.append(Song(song))
        return songs


class Song(object):
    """Class for song abstraction.

    Args:
      song (dict): Song dictionary.

    Attributes:
      _id (str): Song ObjectId.
      _title (str): Song title.
      _owner (str): user Id
      _text (str): Song data itself (lyrics and chords).
      _description (str): Song description.
      _authors (list): Dict of lists of Author ObjectId strings.
      _interpreters (list): List of Interpreter ObjectId strings.
      _visibility (str): Song visibility status
    """

    def __init__(self, song):
        self._id = song['_id']
        self._title = song['title']
        self._owner = song['owner']
        self._text = song['text']
        self._authors = song['authors']
        self._description = song['description']
        self._interpreters = song['interpreters']
        self._visibility = song['visibility']
        self._approved = song['approved']
        self._export_cache = song['export_cache']

    def serialize(self, update=False):
        """Serialize song data for database operations.

        Args:
          update (bool, optional): Determines whether method returns only
            update attributes or data for new database entry.
        """

        song = {
            'title': self._title,
            'owner': self._owner,
            'text': self._text,
            'authors': self._authors,
            'description': self._description,
            'interpreters': self._interpreters,
            'visibility': self._visibility,
            'approved': self._approved,
            'export_cache': self._export_cache
        }

        if not update:
            song['_id'] = self._id

        return song

    def get_serialized_data(self, simple=False):
        if simple:
            return {
                'id': str(self._id),
                'title': self._title,
                'owner': self._owner,
                'interpreters': self._interpreters,
                'visibility': self._visibility
            }

        return {
            'id': str(self._id),
            'created': self._id.generation_time,
            'title': self._title,
            'owner': self._owner,
            'text': self._text,
            'description': self._description,
            'authors': self._authors,
            'interpreters': self._interpreters,
            'visibility': self._visibility,
            'approved': self._approved
        }

    def get_id(self):
        return str(self._id)

    def get_creation_date(self):
        return self._id.generation_time

    def get_title(self):
        return self._title

    def get_text(self):
        return self._text

    def get_authors(self):
        return self._authors

    def get_interpreters(self):
        return self._interpreters

    def get_description(self):
        return self._description

    def get_owner(self):
        return self._owner

    def get_visibility(self):
        return self._visibility

    def _handle_permissions(self, visibility):
        if visibility not in PERMISSION:
            raise AppException(EVENTS.REQUEST_EXCEPTION, 422,
                               (EXCODES.WRONG_VALUE, STRINGS.PERMISSION_WRONG_VALUE, 'visibility'))

        if visibility < self._visibility:
            raise AppException(
                EVENTS.REQUEST_EXCEPTION, 422,
                (EXCODES.WRONG_VALUE, STRINGS.PERMISSION_SMALLER_VALUE, 'visibility'))

        self._visibility = visibility

    def set_data(self, data):
        self._title = data['title'] if 'title' in data else self._title
        self._text = data['text'] if 'text' in data else self._text
        self._description = data['description'] if 'description' in data else self._description
        self._authors = data['authors'] if 'authors' in data else self._authors
        self._interpreters = data['interpreters'] if 'interpreters' in data else self._interpreters
        self._handle_permissions(data['visibility'] if 'visibility' in data else self._visibility)

        # invalidate export cache
        self._export_cache = None

    def generate_sbd_output(self):
        """Generate tex output and return it."""

        # check for cached song translation in export cache
        if self._export_cache is not None:
            return self._export_cache, []

        # translate song lyrics and chords to tex output
        text, log = translate_to_tex(self._text)

        interpreters = []
        for interpreter_id in self._interpreters:
            interpreter = g.model.interpreters.find_one(interpreter_id=interpreter_id)
            interpreters.append(interpreter.get_name())

        # create sbd export data
        filedata = '''\\beginsong{{{}}}[by={{{}}}] {}\endsong'''.format(
            self._title, ", ".join(interpreters), text)

        # save song to export cache if no log information is present
        if not log:
            self._export_cache = filedata
            # save cached song into the database
            g.model.songs.save(self)

        return filedata, log

    def __repr__(self):
        return '<{!r} id={!r} title={!r} interpreters={!r}' \
            .format(self.__class__.__name__, self._id, self._title, self._interpreters)
