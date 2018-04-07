from server.util.structures import ConstantDict


class Events(ConstantDict):
    AUTHOR_NEW = 'AUTHOR NEW'
    AUTHOR_EDIT = 'AUTHOR EDIT'
    AUTHOR_DELETE = 'AUTHOR DELETE'

    INTERPRETER_NEW = 'INTERPRETER NEW'
    INTERPRETER_EDIT = 'INTERPRETER EDIT'
    INTERPRETER_DELETE = 'INTERPRETER DELETE'

    SONG_NEW = 'SONG NEW'
    SONG_EDIT = 'SONG EDIT'
    SONG_DELETE = 'SONG DELETE'

    VARIANT_NEW = 'VARIANT NEW'
    VARIANT_EDIT = 'VARIANT EDIT'
    VARIANT_DELETE = 'VARIANT DELETE'

    SONGBOOK_NEW = 'SONGBOOK NEW'
    SONGBOOK_EDIT = 'SONGBOOK EDIT'
    SONGBOOK_DELETE = 'SONGBOOK DELETE'
    SONGBOOK_SET_SONG = 'SONGBOOK SET SONG'
    SONGBOOK_REMOVE_SONG = 'SONGBOOK REMOVE SONG'

    SONGBOOK_SONG = 'SONGBOOK SONG'

    CLEANUP = 'CLEANUP'

    BASE_EXCEPTION = 'BASE EXCEPTION'
    REQUEST_EXCEPTION = 'REQUEST EXCEPTION'
    VALIDATION_EXCEPTION = 'VALIDATION EXCEPTION'
    COMPILATION_EXCEPTION = 'COMPILATION EXCEPTION'


EVENTS = Events()


class Options(object):

    class Sizes(object):
        A4 = 'A4'
        A5 = 'A5'
        A4_WIDE = 'A4 WIDE'
        A5_WIDE = 'A5 WIDE'

    SIZE = Sizes()


OPTIONS = Options()
size_dict = [OPTIONS.SIZE.A4, OPTIONS.SIZE.A5, OPTIONS.SIZE.A4_WIDE, OPTIONS.SIZE.A5_WIDE]


class Ordering(ConstantDict):
    TITLE = 'title'
    TITLE_DESC = 'title_desc'


ORDERING = Ordering()


class Permissions(ConstantDict):
    PRIVATE = 0
    PUBLIC = 1


PERMISSION = Permissions()


class Tags(ConstantDict):
    CHORUS = '[chorus]'
    VERSE = '[verse]'
    SOLO = '[solo]'
    REC = '[rec]'
    INTRO = '[intro]'
    OUTRO = '[outro]'
    BRIDGE = '[bridge]'
    INTERMEZZO = '[intermezzo]'

    REPETITION_START = '|:'
    REPETITION_END = ':|'

    _SPECIAL = [SOLO, INTRO, OUTRO, BRIDGE, INTERMEZZO]


TAGS = Tags()


class ExceptionCodes(ConstantDict):
    ALREADY_EXISTS = 'already_exists'
    DOES_NOT_EXIST = 'does_not_exist'
    MISSING_FIELD = 'missing_field'
    INVALID_REQUEST = 'invalid_request'
    WRONG_VALUE = 'wrong_value'
    COMPILATION_ERROR = 'compilation_error'
    INSUFFICIENT_PERMISSIONS = 'insufficient_permissions'


EXCODES = ExceptionCodes()
