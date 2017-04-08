# -*- coding: utf-8 -*-

def translate_to_tex(song):

    state_chorus = False
    state_verse = False
    output = ""

    def finish_part(state_chorus, state_verse):
        if state_chorus:
            return "\\endchorus"
        elif state_verse:
            return "\\endverse"
        return ""

    content = [x.strip() for x in song.split('\n')]

    for line in content:
        if line == "#####":
            output += finish_part(state_chorus, state_verse)
            state_chorus = False
            state_verse = True
            output += "\\beginverse"

        elif line == "*****":
            output += finish_part(state_chorus, state_verse)
            state_verse = False
            state_chorus = True
            output += "\\beginchorus"

        elif line == "******":
            output += finish_part(state_chorus, state_verse)
            state_verse = False
            state_chorus = False
            output += "\\repchoruses"
        else:
            line = line.replace('>', '\echo{')
            line = line.replace('<', '}')

            line = line.replace('||{', '\\rrep\\rep{')
            line = line.replace('||', '\\rrep')
            line = line.replace('|', '\\lrep')

            output += line + "\n"

    return output
