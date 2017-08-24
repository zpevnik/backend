def translate_to_tex(song): #FIXME

    state_chorus = False
    state_verse = False
    output = ""

    def finish_part(state_chorus, state_verse):
        return "\\endchorus\n" if state_chorus else \
               "\\endverse\n" if state_verse else \
               ""

    content = [x.strip() for x in song.split('\n')]

    for line in content:
        if line == "##":
            output += finish_part(state_chorus, state_verse)
            state_chorus = False
            state_verse = True
            output += "\\beginverse\n"

        elif line == "**":
            output += finish_part(state_chorus, state_verse)
            state_verse = False
            state_chorus = True
            output += "\\beginchorus\n"

        elif line == "***":
            output += finish_part(state_chorus, state_verse)
            state_verse = False
            state_chorus = False
            #output += "\\repchoruses\n"
            output += "\\beginchorus\n\\endchorus\n"
        else:
            line = line.replace('>', '\echo{')
            line = line.replace('<', '}')

            line = line.replace('||{', '\\rrep\\rep{')
            line = line.replace('||', '\\rrep\n')
            line = line.replace('|', '\\lrep\n')

            output += line + "\n"

    # escape chords so that they are interpered as special symbols
    output = output.replace('[', '\\[')
    # convert quotation marks to LaTeX compatible ones
    output = output.replace('"', '\'\'')
    # escape comment symbols
    output = output.replace('%', '\\%')

    return output
