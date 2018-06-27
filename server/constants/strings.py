class TranslatorStrings(object):
    UNKNOWN_TAG = '[{}] WARNING: Unknown tag {}.'

    ERROR_REPETITION_END_BEFORE_START = '[{}] ERROR: Repetition cannot end before it started.'
    ERROR_REPETITION_OVERLAPPING = '[{}] ERROR: Repetition cannot overlap to other blocks of the song.'
    ERROR_NESTED_REPETITION = '[{}] ERROR: Repetition cannot be nested in other repetition.'
    ERROR_NOT_IMPLEMENTED = '[{}] ERROR: Not yet implemented.'
    ERROR_CHORDS_INSIDE_REC = '[{}] ERROR: Chord tag found inside rec block.'
    ERROR_NO_STARTING_BLOCK = '[0] ERROR: Song must start with some block tag.'
    ERROR_STRING_CONTAINS_FORBIDDEN_CHARACTERS = '[0] ERROR: String contains forbidden characters.'


class Strings(object):
    INSUFFICIENT_PERMISSIONS = 'Na tuto akci nemáš dostatečné oprávnění.'

    POST_REQUEST_ERROR = 'Cannot process POST request.'
    JSON_REQUEST_ERROR = 'Cannot process json request.'

    REQUEST_SONGBOOK_TITLE_MISSING = 'Songbook title is missing.'
    REQUEST_SONGBOOK_SONGS_MISSING = 'Songbook song list is missing.'
    REQUEST_SONGBOOK_OPTIONS_MISSING = 'Songbook options field is missing.'
    REQUEST_SONGBOOK_SONGS_VARIANT_MISSING = 'Songbook variant_id in song list is missing.'

    REQUEST_SONG_TITLE_MISSING = 'Song title is missing.'
    REQUEST_SONG_AUTHORS_MISSING = 'Song authors are missing.'
    REQUEST_SONG_INTERPRETERS_MISSING = 'Song interpreters are missing.'
    REQUEST_SONG_VARIANT_MISSING = 'Song variant key is missing.'

    REQUEST_VARIANT_TITLE_MISSING = 'Song variant title is missing.'
    REQUEST_VARIANT_TEXT_MISSING = 'Song variant text is missing.'
    REQUEST_VARIANT_DESCRIPTION_MISSING = 'Song variant description is missing.'

    REQUEST_INTERPRETER_NAME_MISSING = 'Interpreter name is missing.'
    REQUEST_AUTHOR_NAME_MISSING = 'Author name is missing.'
    REQUEST_PAGE_OOR_ERROR = 'Page number is out of range.'
    REQUEST_PER_PAGE_OOR_ERROR = 'Per page number is out of range.'

    REQUEST_SONGBOOK_ADD_SONG_MISSING = 'Song id is missing.'
    REQUEST_SONGBOOK_SONGS_INVALID = 'Songbook song addition request is wrong.'

    AUTHOR_ALREADY_EXISTS_ERROR = 'Author already exists.'
    AUTHOR_NOT_FOUND_ERROR = 'Author was not found.'
    INTERPRETER_ALREADY_EXISTS_ERROR = 'Interpreter already exists.'
    INTERPRETER_NOT_FOUND_ERROR = 'Interpreter was not found.'
    SONG_NOT_FOUND_ERROR = 'Song was not found.'
    SONG_VARIANT_NOT_FOUND_ERROR = 'Song variant was not found.'
    SONGBOOK_NOT_FOUND_ERROR = 'Songbook was not found.'
    USER_NOT_FOUND_ERROR = 'User was not found.'

    SONGBOOK_SONG_SUCCESS = 'Písňe ve zpěvníku byly úspěšně upraveny.'

    SONGBOOK_OPTIONS_ERROR = 'Cannot process songbook options.'
    SONGBOOK_OPTIONS_SIZE_ERROR = 'Songbook size has invalid value.'

    COMPILATION_ERROR = 'Error occured during latex compilation.'

    PERMISSION_WRONG_VALUE = 'Permission has wrong value.'
    PERMISSION_EDIT_HIGHER_THAN_VIEW = 'Edit permission has grater value than view permission.'
    PERMISSION_SMALLER_VALUE = 'Permission cannot be changed to more restrictive.'

    TRANSLATOR = TranslatorStrings()


STRINGS = Strings()
