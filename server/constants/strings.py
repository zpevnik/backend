class TranslatorStrings(object):
    UNKNOWN_TAG = '[{}] WARNING: Unknown tag {}.'
    IGNORING_INFO = '[{}] WARNING: Ignoring additional info of {} tag.'

    ERROR_CHORUS_OVERLAPPING = '[{}] ERROR: Chorus cannot start or end when other sections are active.'
    ERROR_VERSE_OVERLAPPING = '[{}] ERROR: Verse cannot start or end when other sections are active.'
    ERROR_ECHO_OVERLAPPING = '[{}] ERROR: Echo cannot start or end during solo section.'
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

CHORDS = [
    'A', 'A#', 'A#4', 'A#7', 'A#dim', 'A#m', 'A#m7', 'A#maj7', 'A+', 'A/D', 'A/F#', 'A/G#', 'A11',
    'A13', 'A4', 'A6', 'A7', 'A7(9+)', 'A7+', 'A7sus4', 'A9', 'Ab', 'Ab+', 'Ab11', 'Ab4', 'Ab7',
    'Abdim', 'Abm', 'Abm7', 'Abmaj7', 'Adim', 'Am', 'Am(7#)', 'Am(add9)', 'Am/G', 'Am6', 'Am7',
    'Am7sus4', 'Am9', 'Amaj7', 'Asus', 'B', 'B(addE)', 'B+', 'B/F#', 'B11', 'B11/13', 'B13', 'B4',
    'B7', 'B7#9', 'B7+', 'B9', 'BaddE/F#', 'Bb+', 'Bb11', 'Bb6', 'Bb9', 'Bbm9', 'Bm', 'Bm(maj7)',
    'Bm6', 'Bm7', 'Bm7b5', 'Bmaj', 'Bmsus9', 'C', 'C#', 'C#(add9)', 'C#4', 'C#7', 'C#m', 'C#m7',
    'C#maj', 'C(add9)', 'C/B', 'C11', 'C4', 'C7', 'C9', 'C9(11)', 'Cadd2/B', 'Cm', 'Cm11', 'Cm7',
    'Cmaj', 'Cmaj7', 'Csus2', 'Csus9', 'D', 'D#', 'D#4', 'D#7', 'D#m', 'D#m7', 'D#maj7', 'D(add9)',
    'D/A', 'D/B', 'D/C', 'D/C#', 'D/E', 'D/G', 'D11', 'D4', 'D5/E', 'D6', 'D7', 'D7#9', 'D7sus2',
    'D7sus4', 'D9', 'D9add6', 'Dm', 'Dm#7', 'Dm/A', 'Dm/B', 'Dm/C', 'Dm/C#', 'Dm7', 'Dm9', 'Dmaj7',
    'Dsus2', 'E', 'E11', 'E5', 'E6', 'E7', 'E7#9', 'E7(5b)', 'E7(b9)', 'E9', 'Eb(add9)', 'Em',
    'Em(add9)', 'Em(sus4)', 'Em/B', 'Em/D', 'Em6', 'Em7', 'Emaj7', 'Esus', 'Esus4', 'F', 'F#',
    'F#+', 'F#/E', 'F#11', 'F#4', 'F#7', 'F#9', 'F#m', 'F#m6', 'F#m7-5', 'F#maj', 'F#maj7',
    'F(add9)', 'F/A', 'F/C', 'F/G', 'F11', 'F4', 'F6', 'F7', 'F7/A', 'F9', 'FaddG', 'Fm', 'Fm6',
    'Fm7', 'Fmaj7', 'Fmaj7(+5)', 'Fmaj7/A', 'Fmmaj7', 'G', 'G#m6', 'G(add9)', 'G/A', 'G/B', 'G/D',
    'G/F#', 'G11', 'G4', 'G6', 'G6(sus4)', 'G7', 'G7#9', 'G7(sus4)', 'G9', 'G9(11)', 'Gm', 'Gm/Bb',
    'Gm6', 'Gm7', 'Gmaj7', 'Gmaj7sus4', 'Gmaj9', 'Gsus4'
]
KEYWORDS = ['chorus', 'verse', 'solo', 'repetition', 'echo']
