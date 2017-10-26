import re

from server.constants import CHORDS
from server.constants import STRINGS
from server.constants import KEYWORDS


def translate_to_tex(song):
    _log = []
    _output = []
    _regexp = '\[(\w+)\](\{\d+\})?'
    _context = {
        'solo': False,
        'echo': False,
        'verse': False,
        'chorus': False,
        'repetition': False,
        '_errstate': False
    }

    def process_match(match):
        tag = match.group(1)
        info = match.group(2)

        if tag in KEYWORDS:
            if tag == 'chorus':
                if info:
                    _log.append(STRINGS.TRANSLATOR.IGNORING_INFO.format(_idx, match.group()))
                if _context['solo'] or _context['echo'] or _context['verse'] or _context['repetition']:
                    _log.append(STRINGS.TRANSLATOR.ERROR_CHORUS_OVERLAPPING.format(_idx))
                    _context['_errstate'] = True
                    return ''

                _context['chorus'] = not _context['chorus']
                if _context['chorus']:
                    return '\\beginchorus\n'
                else:
                    return '\\endchorus\n'

            elif tag == 'verse':
                if info:
                    _log.append(STRINGS.TRANSLATOR.IGNORING_INFO.format(_idx, match.group()))
                if _context['solo'] or _context['echo'] or _context['chorus'] or _context['repetition']:
                    _log.append(STRINGS.TRANSLATOR.ERROR_VERSE_OVERLAPPING.format(_idx))
                    _context['_errstate'] = True
                    return ''

                _context['verse'] = not _context['verse']
                if _context['verse']:
                    return '\\beginverse\n'
                else:
                    return '\\endverse\n'

            elif tag == 'solo':
                if info:
                    _log.append(STRINGS.TRANSLATOR.IGNORING_INFO.format(_idx, match.group()))
                _log.append(STRINGS.TRANSLATOR.ERROR_NOT_IMPLEMENTED.format(_idx))
                _context['_errstate'] = True
                return ''

            elif tag == 'echo':
                if info:
                    _log.append(STRINGS.TRANSLATOR.IGNORING_INFO.format(_idx, match.group()))
                if _context['solo']:
                    _log.append(STRINGS.TRANSLATOR.ERROR_ECHO_OVERLAPPING.format(_idx))
                    _context['_errstate'] = True
                    return ''

                _context['echo'] = not _context['echo']
                if _context['echo']:
                    return '\\echo{'
                else:
                    return '}\n'

            elif tag == 'repetition':
                repetition_info = ''
                if info:
                    if not _context['repetition']:
                        _log.append(STRINGS.TRANSLATOR.IGNORING_INFO.format(_idx, match.group()))
                    else:
                        repetition_info = '\\rep{{{}}}'.format(info[1:-1])

                _context['repetition'] = not _context['repetition']
                if _context['repetition']:
                    return '\\lrep\n'
                else:
                    return '\\rrep{}\n'.format(repetition_info)

        elif tag in CHORDS:
            if info:
                _log.append(STRINGS.TRANSLATOR.IGNORING_INFO.format(_idx, match.group()))
            return '[{}]'.format(tag)

        _log.append(STRINGS.TRANSLATOR.UNKNOWN_TAG.format(_idx, match.group()))
        return '[{}]'.format(tag)

    content = [x.strip() for x in song.split('\n')]

    for _idx, line in enumerate(content):
        # translate into LaTeX format
        line = re.sub(_regexp, process_match, line)

        # check whether error occurend during line parsing
        if _context['_errstate']:
            raise TranslationException('\n'.join(_log), 500)

        # escape chords so that they are interpered as special symbols
        line = line.replace('[', '\\[')
        # convert quotation marks to LaTeX compatible ones
        line = line.replace('"', '\'\'')
        # escape comment symbols
        line = line.replace('%', '\\%')

        _output.append(line)

    return '\n'.join(_output), '\n'.join(_log)
