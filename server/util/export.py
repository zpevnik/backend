import os
import subprocess

from server.util import validators
from server.util.misc import generate_random_filename
from server.util.exceptions import CompilationException


def export_song(song):
    filename = generate_random_filename()

    # get sbd song data and save them into aux sbd file
    with open('songs/temp/' + filename + '.sbd', 'w') as file:
        data, log = song.generate_sbd_output()
        file.write(data)

    # generate tex file for given export
    generate_tex_file(filename)

    # export song to pdf file
    link = export_to_pdf(filename)
    return {'link': link, 'log': log}


def export_songbook(songbook):
    log = {}
    filename = generate_random_filename()

    # get sbd song data and save them into aux sbd file
    with open('songs/temp/' + filename + '.sbd', 'a') as file:
        for song_id in songbook.get_songs().keys():
            song = validators.song_existence(song_id)
            data, song_log = song.generate_sbd_output()
            if song_log:
                log[song.get_title()] = song_log

            file.write(data)

    # generate tex file for given export
    generate_tex_file(filename)

    # export songbook to pdf file
    link = export_to_pdf(filename)
    return {'link': link, 'log': log}


def generate_tex_file(filename):
    # read template file
    with open('songs/misc/template.tex', 'r') as sample_file:
        filedata = sample_file.read()

    # replace data in template and save it into tex file
    filedata = filedata.replace('$filename$', filename)
    with open('songs/temp/' + filename + '.tex', 'w') as temp_file:
        temp_file.write(filedata)


def export_to_pdf(filename):

    def error(err, output):
        error = "Error during " + err + ":\n"
        for line in output.decode('latin-1').split("\n"):
            if line.startswith("!"):
                error += line + "\n"

        raise CompilationException(error, 500)

    process = subprocess.Popen(
        ["xelatex", "-halt-on-error", filename + ".tex"], stdout=subprocess.PIPE, cwd='songs/temp')
    output = process.communicate()[0]
    exit_code = process.wait()

    if exit_code:
        error("pdf compilation", output)

    process = subprocess.Popen(
        ["../songidx", filename + ".sxd", filename + ".sbx"],
        stdout=subprocess.PIPE,
        cwd='songs/temp')
    output = process.communicate()[0]
    exit_code = process.wait()

    if exit_code:
        error("index generation", output)

    process = subprocess.Popen(
        ["xelatex", "-halt-on-error", filename + ".tex"], stdout=subprocess.PIPE, cwd='songs/temp')
    output = process.communicate()[0]
    exit_code = process.wait()

    if exit_code:
        error("pdf compilation", output)

    # move finished pdf file to other folder and clean up temp
    os.rename('songs/temp/' + filename + '.pdf', 'songs/done/' + filename + '.pdf')

    # remove all aux files
    for fname in os.listdir('songs/temp'):
        if fname.startswith(filename):
            os.remove(os.path.join('songs/temp', fname))

    if not os.path.isfile("songs/done/" + filename + ".pdf"):
        raise CompilationException('Final pdf file does not exist.', 500)

    return "download/{}.pdf".format(filename)
