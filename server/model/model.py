class Model(object):
    """Main model class, which contains references for all submodels.
    This class initiliaze these submodels.

    Args:
      db: Reference to database.

    Attributes:
      logs (server.model.Logs): Submodel for managing logs.
      users (server.model.Users): Submodel for managing users.
      songs (server.model.Songs): Submodel for managing songs.
      authors (server.model.Authors): Submodel for managing authors.
      songbooks (server.model.Songbooks): Submodel for managing songbooks.
      interpreters (server.model.Interpreters): Submodel for managing interpreters.
    """

    def __init__(self, db):
        from server.model.logs import Logs
        from server.model.users import Users
        from server.model.songs import Songs
        from server.model.authors import Authors
        from server.model.songbooks import Songbooks
        from server.model.interpreters import Interpreters

        self.logs = Logs(model=self, db=db)
        self.users = Users(model=self, db=db)
        self.songs = Songs(model=self, db=db)
        self.authors = Authors(model=self, db=db)
        self.songbooks = Songbooks(model=self, db=db)
        self.interpreters = Interpreters(model=self, db=db)
