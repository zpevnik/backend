import pymongo

from bson import ObjectId
from flask import g

from server.util import validators
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
          data (dict): Song data dictionary containing 'title',
            'authors', 'interpreters' dictionary key.

        Returns:
          Song: Instance of the new song.
        """
        song = Song({
            '_id': ObjectId(),
            'title': data['title'],
            'authors': data['authors'] if 'authors' in data else {
                'lyrics': [],
                'music': []
            },
            'interpreters': data['interpreters'] if 'interpreters' in data else [],
            'approved': False
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
        Only songs with at least one variant reachable by user are returned.

        Returns:
          list: List of Song instances satisfying the query.
        """
        reachable_songs = g.model.variants.find_reachable_song_ids(user_id)

        query_array = []
        for res in reachable_songs:
            query_array.append(ObjectId(res))

        if query is None or query == "":
            doc = self._collection.find({'_id': {"$in": query_array}})
        else:
            doc = self._collection.find({'_id': {"$in": query_array},
                                         '$text': {'$search': query}},
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
      _authors (list): Dict of lists of Author ObjectId strings.
      _interpreters (list): List of Interpreter ObjectId strings.
      _approved (bool): Whether song was approved for public display (not used right now)
    """

    def __init__(self, song):
        self._id = song['_id']
        self._title = song['title']
        self._authors = song['authors']
        self._interpreters = song['interpreters']
        self._approved = song['approved']

    def serialize(self, update=False):
        """Serialize song data for database operations.

        Args:
          update (bool, optional): Determines whether method returns only
            update attributes or data for new database entry.
        """

        song = {
            'title': self._title,
            'authors': self._authors,
            'interpreters': self._interpreters,
            'approved': self._approved
        }

        if not update:
            song['_id'] = self._id

        return song

    def get_serialized_data(self, user_id):
        variants = []
        variant_res = g.model.variants.find_filtered(user_id, song_id=str(self._id))
        for variant in variant_res:
            variants.append(variant.get_serialized_data())

        return {
            'id': str(self._id),
            'created': self._id.generation_time,
            'title': self._title,
            'authors': self._authors,
            'interpreters': self._interpreters,
            'approved': self._approved,
            'variants': variants
        }

    def get_simplified_variant_data(self, variant_id):
        variant = validators.song_variant_existence(variant_id)

        return {
            'id': str(self._id),
            'title': self._title,
            'interpreters': self._interpreters,
            'variant': variant['id'],
            'owner': variant['owner'],
            'visibility': variant['visibility']
        }

    def get_id(self):
        return str(self._id)

    def get_creation_date(self):
        return self._id.generation_time

    def get_title(self):
        return self._title

    def get_authors(self):
        return self._authors

    def get_interpreters(self):
        return self._interpreters

    def set_data(self, data):
        self._title = data['title'] if 'title' in data else self._title
        self._authors = data['authors'] if 'authors' in data else self._authors
        self._interpreters = data['interpreters'] if 'interpreters' in data else self._interpreters

        # clear export cache for songs variants
        variants = g.model.variants.find(song_id=self.get_id())
        for variant in variants:
            variant.invalidate_cache()
            g.model.variants.save(variant)

    def __repr__(self):
        return '<{!r} id={!r} title={!r} interpreters={!r}' \
            .format(self.__class__.__name__, self._id, self._title, self._interpreters)
