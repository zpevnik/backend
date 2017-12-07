import re

from server.constants import CHORDS
from server.constants import STRINGS
from server.constants import KEYWORDS


def translate_to_tex(song):
    _log = []
    _output = []
    _regexp = '(\[\w+\]|\|:|:\|)([0-9]+)?'
    _context = {
        'echo': False,
        'verse': False,
        'chorus': False,
        'repetition': False
    } # yapf: disable

    def finish_part():
        if _context['repetition']:
            _log.append(STRINGS.TRANSLATOR.ERROR_REPETITION_OVERLAPPING.format(_idx))

        if _context['echo']:
            _context['verse'] = False
            return '}'

        if _context['verse']:
            _context['verse'] = False
            return '\\endverse'

        elif _context['chorus']:
            _context['chorus'] = False
            return '\\endchorus'

        return ''

    def process_match(match):
        _result = []

        tag = match.group(1)
        info = match.group(2)

        if tag.lower() in TAGS:

            if tag == TAGS.CHORUS:
                _result.append(finish_part())
                _result.append('\\beginchorus')

                _context['chorus'] = True

            elif tag == TAGS.VERSE:
                _result.append(finish_part())
                _result.append('\\beginverse')

                _context['verse'] = True

            elif tag in TAGS._SPECIAL:
                _result.append(finish_part())
                _result.append('\\*beginverse')

                _context['verse'] = True

            elif tag == TAGS.ECHO:
                _result.append(finish_part())
                _result.append('\\echo{')

                _context['echo'] = True

            elif tag == TAGS.REPETITION_START:
                if _context['repetition']:
                    _log.append(STRINGS.TRANSLATOR.ERROR_NESTED_REPETITION.format(_idx))
                _result.append('\\lrep')

                _context['repetition'] = True

            elif tag == TAGS.REPETITION_END:
                if not _context['repetition']:
                    _log.append(STRINGS.TRANSLATOR.ERROR_REPETITION_END_BEFORE_START.format(_idx))

                count = info if info else 1
                _result.append('\\rrep{}'.format(count))

                _context['repetition'] = False

        elif tag in CHORDS:
            _result.append('[{}]'.format(tag))

        else:
            _log.append(STRINGS.TRANSLATOR.UNKNOWN_TAG.format(_idx, match.group()))

        return ''.join(_result)

    content = [x.strip() for x in song.split('\n')]

    for _idx, line in enumerate(content):
        # translate into LaTeX format
        line = re.sub(_regexp, process_match, line)

        # escape chords so that they are interpered as special symbols
        line = line.replace('[', '\\[')
        # convert quotation marks to LaTeX compatible ones
        line = line.replace('"', '\'\'')
        # escape comment symbols
        line = line.replace('%', '\\%')

        _output.append(line)

    return '\n'.join(_output), '\n'.join(_log)
