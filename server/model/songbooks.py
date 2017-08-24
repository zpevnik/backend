from datetime import datetime

from server.util import generate_random_uuid
from server.util import uuid_from_str
from server.util import uuid_to_str

from server.constants import permission_dict


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
            '_id': generate_random_uuid(),
            'created': datetime.utcnow(),
            'title': data['title'],
            'owner': data['owner'],
            'owner_unit': data['owner_unit'],
            'visibility': data['visibility'],
            'edit_perm': data['edit_perm'],
            'songs': {},
        })
        self._collection.insert(songbook.serialize())

        return songbook

    def save(self, songbook):
        """Save songbook into the database.

        Args:
          songbook (Songbook): Instance of the songbook.
        """
        self._collection.update(
            {'_id': uuid_from_str(songbook.get_id())},
            {'$set': songbook.serialize(update=True)}
        )

    def delete(self, songbook):
        """Delete songbook from the database.

        Args:
          songbook (Songbook): Instance of the songbook.
        """
        self._collection.delete_one(
            {'_id': uuid_from_str(songbook.get_id())}
        )

    def find_special(self, data): # FIXME
        """Find songbooks from the database based on query and page the result.

        Args in dict:
          query (str): Query string.
          page (int): Result page number.
          per_page (int): Number of songbooks per search result.
          user (str): user UUID
          unit (str): Unit UUID

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
          songbook_id (str, optional): Songbook UUID.
          title (str, optional): Title of the songbook.

        Returns:
          Songbook: One Songbook or None if it does not exist.
        """
        query = {}
        if songbook_id is not None:
            query['_id'] = uuid_from_str(songbook_id)
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
      _id (str): Songbook UUID.
      _created (str): Timestamp of the songbook creation.
      _title (str): Songbook title.
      _songs (dict): Songs contained in this songbook.
      _owner (str): user UUID
      _owner_unit (str): Unit UUID
      _visibility (str): Songbook visibility status
      _edit_perm (str): Editing permission status
    """

    def __init__(self, songbook):
        self._id = uuid_to_str(songbook['_id'])
        self._created = songbook['created']
        self._title = songbook['title']
        self._songs = songbook['songs']
        self._owner = songbook['owner']
        self._owner_unit = songbook['owner_unit']
        self._visibility = songbook['visibility']
        self._edit_perm = songbook['edit_perm']

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
            'owner_unit': self._owner_unit,
            'visibility': self._visibility,
            'edit_perm': self._edit_perm
        }

        if not update:
            songbook['_id'] = uuid_from_str(self._id)
            songbook['created'] = self._created

        return songbook

    def get_serialized_data(self):
        return {
            'id': self._id,
            'created': self._created.isoformat(),
            'title': self._title,
            'songs': self._songs,
            'owner': self._owner,
            'owner_unit': self._owner_unit,
            'visibility': self._visibility,
            'edit_perm': self._edit_perm
        }

    def get_id(self):
        return self._id

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

    def set_data(self, data):
        self._title = data['title'] if 'title' in data else self._title
        if 'visibility' in data:
            if data['visibility'] in permission_dict:
                self._visibility = data['visibility']
        if 'edit_perm' in data:
            if data['edit_perm'] in permission_dict:
                self._edit_perm = data['edit_perm']

    def add_song(self, song_id, data):
        self._songs[song_id] = data

    def remove_song(self, song_id):
        self._songs.pop(song_id, None)

    def __repr__(self):
        return '<{!r} id={!r} title={!r}>' \
            .format(self.__class__.__name__, self._id, self._title)
