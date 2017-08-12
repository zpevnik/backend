class Strings(object):
    PERMISSIONS_NOT_SUFFICIENT = 'Na tuto akci nemáš dostatečné oprávnění.'

    POST_REQUEST_ERROR = 'Cannot process POST request.'
    JSON_REQUEST_ERROR = 'Cannot process json request.'

    REQUEST_SONGBOOK_TITLE_MISSING = 'Songbook title is missing.'
    REQUEST_SONG_TITLE_MISSING = 'Song title is missing.'
    REQUEST_SONG_TEXT_MISSING =  'Song text is missing.'
    REQUEST_SONG_DESCRIPTION_MISSING =  'Song description is missing.'
    REQUEST_SONG_AUTHORS_MISSING =  'Song authors are missing.'
    REQUEST_SONG_INTERPRETERS_MISSING =  'Song interpreters are missing.'
    REQUEST_AUTHOR_NAME_MISSING = 'Author name is missing.'
    REQUEST_PAGE_OOR_ERROR = 'Page number is out of range.'
    REQUEST_PER_PAGE_OOR_ERROR = 'Per page number is out of range.'

    AUTHOR_ALREADY_EXISTS_ERROR = 'Author already exists.'
    AUTHOR_NOT_FOUND_ERROR = 'Author was not found.'
    SONG_NOT_FOUND_ERROR = 'Song was not found.'
    SONGBOOK_NOT_FOUND_ERROR = 'Songbook was not found.'

    SONGBOOK_ADD_SONG_SUCCESS = 'Píseň byla úspěšně přidána do zpěvníku.'

STRINGS = Strings()
