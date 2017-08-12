from datetime import datetime

from server.util import generate_random_uuid
from server.util import uuid_from_str
from server.util import uuid_to_str


class Logs(object):
    """Collection for managing CRUD operation in database for logs.

    Args:
      model (server.model.Model): Reference to model.
      db (pymongo.MongoClient): Reference to database.

    Attributes:
      _model (server.model.Model): Reference to model.
      _db: Reference to database.
      _collection: Reference to collection in database for this class.
    """

    COLLECTION_NAME = 'logs'

    def __init__(self, model, db):
        self._model = model
        self._db = db
        self._collection = db[self.COLLECTION_NAME]

    def create_log(self, data):
        """Create new log and insert it into database.

        Args:
          data (dict): Log data containing 'event', 'data' and 'user' dictionary key.

        Returns:
          Log: Instance of the new log.
        """
        log = Log({
            '_id': generate_random_uuid(),
            'created': datetime.utcnow(),
            'data': data['data'],
            'event': data['event'],
            'user': data['user']
        })
        self._collection.insert(log.serialize())

        return log

    def find(self, event=None, user=None): #TODO
        """Find logs in the database based on the query parameters.

        Args:
          event (str): event type.
          user (str): User UUID.

        If the query parameters are empty, whole database is returned.

        Returns:
          list: List of Log instances satisfying the query.
        """
        loc = locals()
        loc.pop('self', None)
        criteria = {k:loc[k] for k in loc if loc[k] != None}
        doc = self._collection.find(criteria)

        logs = [Log(x) for x in doc]
        return logs


class Log(object):
    """Class for log abstraction.

    Args:
      log (dict): Log dictionary.

    Attributes:
      _id (str): Log UUID.
      _user (str): User UUID.
      _created (str): Timestamp of the log creation.
      _event (str): Event type.
      _data (dict): Additional data for this event.
    """

    def __init__(self, log):
        self._id = uuid_to_str(log['_id'])
        self._created = log['created']
        self._event = log['event']
        self._user = log['user']
        self._data = log['data']

    def serialize(self):
        return {
            '_id': uuid_from_str(self._id),
            'user': self._user,
            'data': self._data,
            'event': self._event,
            'created': self._created
        }

    def get_serialized_data(self):
        return {
            'id': self._id,
            'user': self._user,
            'data': self._data,
            'event': self._event,
            'created': self._created.isoformat()
        }

    def get_id(self):
        return self._id

    def __repr__(self):
        return '<{!r} id={!r} created={!r} event={!r} user={!r}' \
            .format(self.__class__.__name__, self._id, self._created, self._event, self._user)
