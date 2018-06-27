from bson import ObjectId
from flask import g

from server.util import AppException
from server.util import SongTemplate
from server.util import translate_to_tex
from server.util import validators

from server.constants import EVENTS
from server.constants import EXCODES
from server.constants import STRINGS
from server.constants import PERMISSION


class Variants(object):
    """Collection for managing CRUD operation in database for variants.

    Args:
      model (server.model.Model): Reference to model.
      db (pymongo.MongoClient): Reference to database.

    Attributes:
      _model (server.model.Model): Reference to model.
      _db: Reference to database.
      _collection: Reference to collection in database for this class.
    """

    COLLECTION_NAME = 'variants'

    def __init__(self, model, db):
        self._model = model
        self._db = db
        self._collection = db[self.COLLECTION_NAME]

    def create_variant(self, data):
        """Create new variant and insert it into database.

        Args:
          data (dict): Song variant data dictionary containing 'owner', 'text',
            'description', 'title' and 'visibility' dictionary key.

        Returns:
          Variant: Instance of the new variant.
        """
        variant = Variant({
            '_id': ObjectId(),
            'song_id': ObjectId(data['song_id']),
            'owner': data['owner'],
            'title': data['title'],
            'text': data['text'] if 'text' in data else '',
            'description': data['description'] if 'description' in data else '',
            'visibility': data['visibility'],
            'export_cache': None
        })
        self._collection.insert_one(variant.serialize())

        return variant

    def save(self, variant):
        """Save variant into the database.

        Args:
          variant (Variant): Instance of the variant.
        """
        self._collection.update_one({'_id': variant._id}, {'$set': variant.serialize(update=True)})

    def delete(self, variant):
        """Delete variant from the database.

        Args:
          variant (Variant): Instance of the variant.
        """
        self._collection.delete_one({'_id': variant._id})

    def find(self, song_id=None):
        """Find all variants in the database based on given song id."""
        query = {}
        if song_id is not None:
            query['song_id'] = ObjectId(song_id)

        doc = self._collection.find(query)

        variants = []
        for variant in doc:
            variants.append(Variant(variant))

        return variants

    def find_filtered(self, user_id, song_id=None):
        """Find songs from the database based on query and permissions.

        Args:
          user_id (str): user Id string.
          song_id (str): Optional song id.

        All returned song variants are accessible by this user.

        Returns:
          list: List of song Variants instances satisfying the song_id.
        """
        doc = self._collection.find({
            '$and': [{
                'song_id': ObjectId(song_id)
            }, {
                '$or': [{
                    'owner': user_id
                }, {
                    'visibility': {
                        "$gte": PERMISSION.PUBLIC
                    }
                }]
            }]
        })

        variants = []
        for variant in doc:
            variants.append(Variant(variant))
        return variants

    def find_one(self, variant_id=None):
        """Find one song variant based on given arguments.

        Args:
          variant_id (str, optional): Variant ObjectId string.

        Returns:
          Author: One song Variant or None if it does not exist.
        """
        query = {}
        if variant_id is not None:
            query['_id'] = ObjectId(variant_id)

        doc = self._collection.find_one(query)
        if not doc:
            return None

        return Variant(doc)

    def find_reachable_song_ids(self, user_id):
        """Find song_ids of variants reachable by given user.

        Args:
          user_id (str): user Id string.

        Returns:
          list: List of song ids which have some variants for given user.
        """
        doc = self._db.command({
            "distinct": self.COLLECTION_NAME,
            "query": {
                '$or': [{
                    'owner': user_id
                }, {
                    'visibility': {
                        "$gte": PERMISSION.PUBLIC
                    }
                }]
            },
            "key": "song_id"
        })

        return doc['values']

    def find_extended_songbook_items(self, items):
        query_array = []
        for item in items:
            query_array.append(ObjectId(item['variant_id']))

        # Mongo currently doesn't support translation between str and ObjectId
        # in lookup and therefore song_id must be saved as ObjectId
        # for this to work.

        doc = self._collection.aggregate([{
            '$match': {
                '_id': {
                    "$in": query_array
                }
            }
        }, {
            '$lookup': {
                'from': "songs",
                'localField': "song_id",
                'foreignField': "_id",
                'as': "song"
            }
        }])

        extended_items = []
        for item in doc:
            extended_items.append({
                'variant_id': str(item['_id']),
                'owner': item['owner'],
                'title': item['title'],
                'visibility': item['visibility'],
                'song': {
                    'song_id': str(item['song_id']),
                    'title': item['song'][0]['title'],
                    'interpreters': item['song'][0]['interpreters']
                },
                'order': next((a['order'] for a in items if a['variant_id'] == str(item['_id'])), 0)
            }) # yapf: disable

        return extended_items


class Variant(object):
    """Class for variant abstraction.

    Args:
      variant (dict): Variant dictionary.

    Attributes:
      _id (str): Variant ObjectId.
      _song_id (str): Song Id
      _owner (str): user Id
      _text (str): Variant data itself (lyrics and chords).
      _description (str): Variant description.
      _visibility (str): Variant visibility status
    """

    def __init__(self, variant):
        self._id = variant['_id']
        self._song_id = variant['song_id']
        self._owner = variant['owner']
        self._title = variant['title']
        self._text = variant['text']
        self._description = variant['description']
        self._visibility = variant['visibility']
        self._export_cache = variant['export_cache']

    def serialize(self, update=False):
        """Serialize variant data for database operations.

        Args:
          update (bool, optional): Determines whether method returns only
            update attributes or data for new database entry.
        """

        variant = {
            'text': self._text,
            'title': self._title,
            'description': self._description,
            'visibility': self._visibility,
            'export_cache': self._export_cache
        }

        if not update:
            variant['_id'] = self._id
            variant['song_id'] = self._song_id
            variant['owner'] = self._owner

        return variant

    def get_serialized_data(self):
        return {
            'id': str(self._id),
            'created': self._id.generation_time,
            'song_id': str(self._song_id),
            'owner': self._owner,
            'title': self._title,
            'text': self._text,
            'description': self._description,
            'visibility': self._visibility
        }

    def get_id(self):
        return str(self._id)

    def get_creation_date(self):
        return self._id.generation_time

    def get_text(self):
        return self._text

    def get_song_id(self):
        return str(self._song_id)

    def get_title(self):
        return self._title

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
        self._handle_permissions(data['visibility'] if 'visibility' in data else self._visibility)

        # invalidate or reset export cache
        self._export_cache = data['export_cache'] if 'export_cache' in data else None

    def get_output_template(self):
        """Generate tex output template and return it."""

        # generate latex output if export cache is empty
        if self._export_cache is None:
            #self._export_cache = song_format(self._text)

            # get parent song of this variant
            song = g.model.songs.find_one(song_id=str(self._song_id))

            # translate song lyrics and chords to tex output (error throws exception)
            latex_output = validators.song_format({'text': self._text})

            # get all interpreters of this song
            interpreters = []
            for interpreter_id in song.get_interpreters():
                interpreter = g.model.interpreters.find_one(interpreter_id=interpreter_id)
                interpreters.append(interpreter.get_name())

            # save variant to export cache
            self._export_cache = {
                'title': song.get_title(),
                'interpreters': interpreters,
                'song': latex_output
            }

            # save cached song into the database
            g.model.variants.save(self)

        return SongTemplate(self._export_cache)

    def __repr__(self):
        return '<{!r} id={!r} owner={!r} _description={!r}' \
            .format(self.__class__.__name__, self._id, self._owner, self._description)
