class Model(object):
    """Main model class, which contains references for all submodels.
    This class initiliaze these submodels.

    Args:
      db: Reference to database.

    Attributes:
      users (server.model.Users): Submodel for managing users.
      songs (server.model.Songs): Submodel for managing songs.
      authors (server.model.Authors): Submodel for managing authors.
      songbooks (server.model.Songbooks): Submodel for managing songbooks.
    """

    def __init__(self, db):
        from server.model.users import Users
        from server.model.songs import Songs
        from server.model.authors import Authors
        from server.model.songbooks import Songbooks

        self.users = Users(model=self, db=db)
        self.songs = Songs(model=self, db=db)
        self.authors = Authors(model=self, db=db)
        self.songbooks = Songbooks(model=self, db=db)
