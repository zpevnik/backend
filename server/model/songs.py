from bson import ObjectId
from flask import g

from server.util import translate_to_tex
from server.constants import permission_dict


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
            'description', 'authors', 'variants', 'interpreters', 'owner_unit',
            'visibility' and 'edit_perm' dictionary key.

        Returns:
          Song: Instance of the new song.
        """
        song = Song({
            '_id': ObjectId(),
            'title': data['title'],
            'owner': data['owner'],
            'owner_unit': data['owner_unit'],
            'text': data['text'] if 'text' in data else '',
            'description': data['description'] if 'description' in data else '',
            'authors': data['authors'] if 'authors' in data else {
                'lyrics': [],
                'music': []
            },
            'interpreters': data['interpreters'] if 'interpreters' in data else [],
            'visibility': data['visibility'],
            'edit_perm': data['edit_perm'],
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
        """Find all authors in the database."""
        doc = self._collection.find({})

        songs = []
        for song in doc:
            songs.append(Song(song))

        return songs

    def find_special(self, data):
        """Find songs in the database based on query and page the result.

        Args in dict:
          query (str): Query string.
          page (int): Result page number.
          per_page (int): Number of songbooks per search result.
          user (str): user Id string
          unit (str): Unit Id string

        If the query string is empty, whole database is returned (and paged).

        Returns:
          list: List of Songs instances satisfying the query.
        """
        if data['query'] is None or data['query'] == "":
            doc = self._collection.find({}).skip(data['page'] * data['per_page']) \
                                  .limit(data['per_page'])
        else:
            doc = self._collection.find({'$text':{'$search': data['query']}},
                                        {'score': {'$meta': "textScore"}}) \
                                  .sort([('score', {'$meta': 'textScore'})]) \
                                  .skip(data['page'] * data['per_page']).limit(data['per_page'])

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
      _owner_unit (str): Unit Id
      _visibility (str): Song visibility status
      _edit_perm (str): Editing permission status
    """

    def __init__(self, song):
        self._id = song['_id']
        self._title = song['title']
        self._owner = song['owner']
        self._text = song['text']
        self._authors = song['authors']
        self._description = song['description']
        self._interpreters = song['interpreters']
        self._owner_unit = song['owner_unit']
        self._visibility = song['visibility']
        self._edit_perm = song['edit_perm']
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
            'owner_unit': self._owner_unit,
            'visibility': self._visibility,
            'edit_perm': self._edit_perm,
            'export_cache': self._export_cache
        }

        if not update:
            song['_id'] = self._id

        return song

    def get_serialized_data(self):
        return {
            'id': str(self._id),
            'created': self._id.generation_time,
            'title': self._title,
            'owner': self._owner,
            'owner_unit': self._owner_unit,
            'text': self._text,
            'description': self._description,
            'authors': self._authors,
            'interpreters': self._interpreters,
            'visibility': self._visibility,
            'edit_perm': self._edit_perm,
            'export_cache': self._export_cache
        }

    def get_id(self):
        return str(self._id)

    def get_creation_date(self):
        return self._id.generation_time

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

    def get_owner_unit(self):
        return self._owner_unit

    def get_visibility(self):
        return self._visibility

    def get_edit_perm(self):
        return self._edit_perm

    def set_data(self, data):
        self._title = data['title'] if 'title' in data else self._title
        self._text = data['text'] if 'text' in data else self._text
        self._description = data['description'] if 'description' in data else self._description
        self._authors = data['authors'] if 'authors' in data else self._authors
        self._interpreters = data['interpreters'] if 'interpreters' in data else self._interpreters
        if 'visibility' in data:
            if data['visibility'] in permission_dict:
                self._visibility = data['visibility']
        if 'edit_perm' in data:
            if data['edit_perm'] in permission_dict:
                self._edit_perm = data['edit_perm']

        # invalidate export cache
        self._export_cache = None

    def generate_sbd_output(self):
        """Generate tex output and return it."""

        # check for cached song translation in export cache
        if self._export_cache is not None:
            return self._export_cache, []

        # translate song lyrics and chords to tex output
        text, log = translate_to_tex(self._text)

        authors = []
        for author_id in self._interpreters:
            author = g.model.authors.find_one(author_id=author_id)
            authors.append(author.get_name())

        # create sbd export data
        filedata = '''\\beginsong{{{}}}[by={{{}}}] {}\endsong'''.format(
            self._title, ", ".join(authors), text)

        # save song to export cache if no log information is present
        self._export_cache = filedata if not log else None

        return filedata, log

    def __repr__(self):
        return '<{!r} id={!r} title={!r} authors={!r} interpreters={!r}' \
            .format(self.__class__.__name__, self._id, self._title,
                    self._authors, self._interpreters)
