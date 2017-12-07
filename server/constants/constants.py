from server.util import ConstantDict


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


class Permissions(ConstantDict):
    PRIVATE = 'private'
    UNIT = 'unit'
    WAITING = 'waiting'
    PUBLIC = 'public'


PERMISSION = Permissions()


class Tags(ConstantDict):
    CHORUS = '[chorus]'
    VERSE = '[verse]'
    SOLO = '[solo]'
    ECHO = '[echo]'
    INTRO = '[intro]'
    OUTRO = '[outro]'
    BRIDGE = '[bridge]'
    INTERMEZZO = '[intermezzo]'

    REPETITION_START = '|:'
    REPETITION_END = ':|'

    _SPECIAL = [SOLO, INTRO, OUTRO, BRIDGE, INTERMEZZO]


TAGS = Tags()

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
