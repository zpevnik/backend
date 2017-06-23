from datetime import datetime
from flask import g

from server.util import generate_random_uuid
from server.util import uuid_from_str
from server.util import uuid_to_str
from server.util import translate_to_tex
from server.util.exceptions import ClientException


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
          data (dict): Song data dictionary containing 'title', 'text', 'text',
            'authors', 'variants' and 'interpreters' dictionary key.

        Returns:
          Song: Instance of the new song.
        """
        song = Song({
            '_id': generate_random_uuid(),
            'created': datetime.utcnow(),
            'title': data['title'],
            'text': data['text'] if 'text' in data else [],
            'authors': data['authors'] if 'authors' in data else {'lyrics': [], 'music': []},
            'interpreters': data['interpreters'] if 'interpreters' in data else []
        })
        self._collection.insert(song.serialize())

        return song

    def save(self, song):
        """Save song into the database.

        Args:
          song (Song): Instance of the song.
        """
        self._collection.update(
            {'_id': uuid_from_str(song.get_id())},
            {'$set': song.serialize(update=True)}
        )

    def delete(self, song):
        """Delete song from the database.

        Args:
          song (Song): Instance of the song.
        """
        self._collection.delete_one(
            {'_id': uuid_from_str(song.get_id())}
        )

    def find_special(self, query, page, per_page):
        """Find songs in the database based on query and page the result.

        Args:
          query (str): Query string.
          page (int): Result page number.
          per_page (int): Number of songs per search result.

        If the query string is empty, whole database is returned (and paged).

        Returns:
          list: List of Songs instances satisfying the query.
        """
        if query is None or query == "":
            doc = self._collection.find({}).skip(page*per_page).limit(per_page)
        else:
            doc = self._collection.find({'$text':{'$search': query}},
                                        {'score': {'$meta': "textScore"}}) \
                                  .sort([('score', {'$meta': 'textScore'})]) \
                                  .skip(page * per_page).limit(per_page)

        songs = []
        for song in doc:
            songs.append(Song(song))

        return songs

    def find_one(self, song_id=None, title=None):
        """Find one song based on given arguments.

        Args:
          song_id (str, optional): Song UUID.
          title (str, optional): Title of the song.

        Returns:
          Author: One Song or None if it does not exist.
        """
        query = {}
        if song_id is not None:
            query['_id'] = uuid_from_str(song_id)
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
      _id (str): Song UUID.
      _created (str): Timestamp of the song creation.
      _title (str): Song title.
      _text (str): Song data itself (lyrics and chords).
      _authors (list): Dict of lists of Author UUIDs.
      _interpreters (list): List of Interpreter UUIDs.
    """

    def __init__(self, song):
        self._id = uuid_to_str(song['_id'])
        self._created = song['created']
        self._title = song['title']
        self._text = song['text']
        self._authors = song['authors']
        self._interpreters = song['interpreters']

    def serialize(self, update=False):
        """Serialize song data for database operations.

        Args:
          update (bool, optional): Determines whether method returns only
            update attributes or data for new database entry.
        """

        song = {
            'title': self._title,
            'text': self._text,
            'authors': self._authors,
            'interpreters': self._interpreters
        }

        if not update:
            song['_id'] = uuid_from_str(self._id)
            song['created'] = self._created

        return song

    def get_serialized_data(self):
        return {
            'id': self._id,
            'created': self._created.isoformat(),
            'title': self._title,
            'text': self._text,
            'authors': self._authors,
            'interpreters': self._interpreters
        }

    def get_id(self):
        return self._id

    def get_text(self):
        return self._text

    def get_authors(self):
        return self._authors

    def get_interpreters(self):
        return self._interpreters

    def set_title(self, title):
        self._title = title

    def set_text(self, text):
        self._text = text

    def set_authors(self, authors):
        self._authors = authors

    def set_interpreters(self, interpreters):
        self._interpreters = interpreters

    def add_author(self, author_id):
        if author_id in self._authors:
            raise ClientException('Tento autor je jiz k pisni prirazen', 404)

        self._authors.append(author_id)

    def remove_author(self, author_id):
        if author_id not in self._authors:
            raise ClientException('Tento autor neni u pisne prirazen', 404)

        self._authors.remove(author_id)

    def add_interpreter(self, interpreter_id):
        if interpreter_id in self._interpreters:
            raise ClientException('Tento interpret je jiz k pisni prirazen', 404)

        self._interpreters.append(interpreter_id)

    def remove_interpreter(self, interpreter_id):
        if interpreter_id not in self._interpreters:
            raise ClientException('Tento interpret neni u pisne prirazen', 404)

        self._interpreters.remove(interpreter_id)


    def generate_tex(self, filename):
        """Generate tex output and append it to given filename.

        Since this method is appending the code and not overwriting given file,
        it can be called on multiple songs in the row with the same file name.

        Args:
          filename (str): Output file name.
        """
        with open('songs/sample/sample.sbd', 'r') as sample_file:
            filedata = sample_file.read()

        text = translate_to_tex(self.get_text())

        authors = []
        for author_id in self._authors:
            author = g.model.authors.find_one(author_id=author_id)
            authors.append(author.get_fullname())

        filedata = filedata.replace('$title$', self._title)
        filedata = filedata.replace('$authors$', ", ".join(authors))
        filedata = filedata.replace('$song$', text)

        with open('songs/temp/' + filename + '.sbd', 'a') as song_file:
            song_file.write(filedata)


    def __repr__(self):
        return '<{!r} id={!r} title={!r} authors={!r} interpreters={!r}' \
            .format(self.__class__.__name__, self._id, self._title,
                    self._authors, self._interpreters)
