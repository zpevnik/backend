import re

from server.constants import TAGS
from server.constants import STRINGS


def translate_to_tex(song):
    _log = []
    _notes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    _output = []
    _regexp = '(\[\w+\]|\|:|:\|)([0-9]+)?'
    _context = {
        'echo': False,
        'verse': False,
        'chorus': False,
        'repetition': False
    } # yapf: disable

    def _is_chord(chord):
        if chord[1] in _notes:
            return True
        return False

    def _finish_part():
        # check for repetition overlapping to other blocks
        if _context['repetition']:
            _log.append(STRINGS.TRANSLATOR.ERROR_REPETITION_OVERLAPPING.format(_idx))

        # finish and close previous block
        if _context['echo']:
            _context['echo'] = False
            return '}'

        if _context['verse']:
            _context['verse'] = False
            return '\\endverse'

        elif _context['chorus']:
            _context['chorus'] = False
            return '\\endchorus'

        return ''

    def _process_match(match):
        _result = []

        tag = match.group(1)
        info = match.group(2)

        # handle tags and their correct translation
        if tag.lower() in TAGS:

            # transform tag to lowercase
            tag = tag.lower()

            if tag == TAGS.CHORUS:
                _result.append(_finish_part())
                _result.append('\\beginchorus\n')

                _context['chorus'] = True

            elif tag == TAGS.VERSE:
                _result.append(_finish_part())
                _result.append('\\beginverse\n')

                _context['verse'] = True

            elif tag in TAGS._SPECIAL:
                _result.append(_finish_part())
                _result.append('\\beginverse*\n')

                _context['verse'] = True

            elif tag == TAGS.ECHO:
                _result.append(_finish_part())
                _result.append('\\echo{')

                _context['echo'] = True

            elif tag == TAGS.REPETITION_START:
                if _context['repetition']:
                    _log.append(STRINGS.TRANSLATOR.ERROR_NESTED_REPETITION.format(_idx))
                _result.append('\\lrep ')

                _context['repetition'] = True

            elif tag == TAGS.REPETITION_END:
                if not _context['repetition']:
                    _log.append(STRINGS.TRANSLATOR.ERROR_REPETITION_END_BEFORE_START.format(_idx))

                count = info if info else 1
                _result.append('\\rrep{{{}}}\n'.format(count))

                _context['repetition'] = False

        # handle chords
        elif _is_chord(tag):
            if _context['echo']:
                _log.append(STRINGS.TRANSLATOR.ERROR_CHORDS_INSIDE_ECHO.format(_idx))

            _result.append(tag)

        else:
            _log.append(STRINGS.TRANSLATOR.UNKNOWN_TAG.format(_idx, match.group()))

        return ''.join(_result)

    content = [x.strip() for x in song.split('\n')]

    for _idx, line in enumerate(content):
        # translate into LaTeX format
        line = re.sub(_regexp, _process_match, line)

        # escape chords so that they are interpered as special symbols
        line = line.replace('[', '\\[')
        # convert quotation marks to LaTeX compatible ones
        line = line.replace('"', '\'\'')
        # escape comment symbols
        line = line.replace('%', '\\%')

        _output.append(line)

    # finish entire song
    _output.append(_finish_part())

    return '\n'.join(_output), '\n'.join(_log)
