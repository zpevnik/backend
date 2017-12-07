class TranslatorStrings(object):
    UNKNOWN_TAG = '[{}] WARNING: Unknown tag {}.'

    ERROR_REPETITION_END_BEFORE_START = '[{}] ERROR: Repetition cannot end before it started.'
    ERROR_REPETITION_OVERLAPPING = '[{}] ERROR: Repetition cannot overlap to other blocks of the song.'
    ERROR_NESTED_REPETITION = '[{}] ERROR: Repetition cannot be nested in other repetition.'
    ERROR_NOT_IMPLEMENTED = '[{}] ERROR: Not yet implemented.'


class Strings(object):
    PERMISSIONS_NOT_SUFFICIENT = 'Na tuto akci nemáš dostatečné oprávnění.'

    POST_REQUEST_ERROR = 'Cannot process POST request.'
    JSON_REQUEST_ERROR = 'Cannot process json request.'

    REQUEST_SONGBOOK_TITLE_MISSING = 'Songbook title is missing.'
    REQUEST_SONG_TITLE_MISSING = 'Song title is missing.'
    REQUEST_SONG_TEXT_MISSING = 'Song text is missing.'
    REQUEST_SONG_DESCRIPTION_MISSING = 'Song description is missing.'
    REQUEST_SONG_AUTHORS_MISSING = 'Song authors are missing.'
    REQUEST_SONG_INTERPRETERS_MISSING = 'Song interpreters are missing.'
    REQUEST_INTERPRETER_NAME_MISSING = 'Interpreter name is missing.'
    REQUEST_AUTHOR_NAME_MISSING = 'Author name is missing.'
    REQUEST_PAGE_OOR_ERROR = 'Page number is out of range.'
    REQUEST_PER_PAGE_OOR_ERROR = 'Per page number is out of range.'

    REQUEST_SONGBOOK_ADD_SONG_MISSING = 'Song id is missing.'

    AUTHOR_ALREADY_EXISTS_ERROR = 'Author already exists.'
    AUTHOR_NOT_FOUND_ERROR = 'Author was not found.'
    INTERPRETER_ALREADY_EXISTS_ERROR = 'Interpreter already exists.'
    INTERPRETER_NOT_FOUND_ERROR = 'Interpreter was not found.'
    SONG_NOT_FOUND_ERROR = 'Song was not found.'
    SONGBOOK_NOT_FOUND_ERROR = 'Songbook was not found.'
    USER_NOT_FOUND_ERROR = 'User was not found.'

    SONGBOOK_SET_SONG_SUCCESS = 'Píseň byla úspěšně upravená do zpěvníku.'
    USER_SET_ACTIVE_SONGBOOK = 'Aktivní zpěvník byl změněn.'

    SONGBOOK_OPTIONS_ERROR = 'Cannot process songbook options.'
    SONGBOOK_OPTIONS_SIZE_ERROR = 'Songbook size has invalid value.'

    TRANSLATOR = TranslatorStrings()


STRINGS = Strings()