import os
import subprocess

from server.app import app
from server.util import validators
from server.util.misc import generate_random_filename
from server.util.exceptions import AppException

from server.constants import EVENTS
from server.constants import EXCODES
from server.constants import STRINGS
from server.constants import DEFAULTS


def export_variant(variant):
    filename = generate_random_filename()

    # get sbd song data and save them into aux sbd file
    with open(app.config['SONGBOOK_TEMP_FOLDER'] + filename + '.sbd', 'wb') as file:
        data, log, _ = variant.generate_sbd_output()
        file.write(data.encode('utf8'))

    # generate tex file for given export
    generate_tex_file(filename, DEFAULTS.SONGBOOK_OPTIONS)

    # export song to pdf file
    link = export_to_pdf(filename)
    return {'link': link, 'log': log}


def export_songbook(songbook):
    # check if songbook is cached
    if songbook.is_cached():
        filename = songbook.get_cached_file(extend=True)

        # check if file really exists
        if os.path.isfile(app.config['SONGBOOK_DONE_FOLDER'] + filename + ".pdf"):
            return {'link': "download/{}.pdf".format(filename), 'log': {}}

    # start export process
    log = {}
    filename = generate_random_filename()

    # get sbd song variant data and save them into aux sbd file
    with open(app.config['SONGBOOK_TEMP_FOLDER'] + filename + '.sbd', 'ab') as file:
        for song_obj in songbook.get_songs():
            variant = validators.song_variant_existence(song_obj['variant_id'])
            data, variant_log, title = variant.generate_sbd_output()
            if variant_log:
                log[title] = variant_log

            file.write(data.encode('utf8'))

    # generate tex file for given export
    generate_tex_file(filename, songbook.get_options())

    # export songbook to pdf file
    link = export_to_pdf(filename)

    # cache songbook
    songbook.cache_file(filename)
    return {'link': link, 'log': log}


def generate_tex_file(filename, options):
    # read template file
    with open('songs/misc/template.tex', 'rb') as sample_file:
        filedata = sample_file.read().decode('utf8')

    # replace data in template and save it into tex file
    filedata = filedata.replace('$filename$', filename)
    with open(app.config['SONGBOOK_TEMP_FOLDER'] + filename + '.tex', 'wb') as temp_file:
        temp_file.write(filedata.encode('utf8'))


def export_to_pdf(filename):

    def error(err, output):
        error = "Error during " + err + ":\n"
        for line in output.decode('latin-1').split("\n"):
            if line.startswith("!"):
                error += line + "\n"

        raise AppException(EVENTS.COMPILATION_EXCEPTION, 500,
                           (EXCODES.COMPILATION_ERROR, STRINGS.COMPILATION_ERROR, error))

    process = subprocess.Popen(
        ["xelatex", "-halt-on-error", filename + ".tex"],
        stdout=subprocess.PIPE,
        cwd=app.config['SONGBOOK_TEMP_FOLDER'])
    output = process.communicate()[0]
    exit_code = process.wait()

    if exit_code:
        error("pdf compilation", output)

    process = subprocess.Popen(
        ["../songidx", filename + ".sxd", filename + ".sbx"],
        stdout=subprocess.PIPE,
        cwd=app.config['SONGBOOK_TEMP_FOLDER'])
    output = process.communicate()[0]
    exit_code = process.wait()

    if exit_code:
        error("index generation", output)

    process = subprocess.Popen(
        ["xelatex", "-halt-on-error", filename + ".tex"],
        stdout=subprocess.PIPE,
        cwd=app.config['SONGBOOK_TEMP_FOLDER'])
    output = process.communicate()[0]
    exit_code = process.wait()

    if exit_code:
        error("pdf compilation", output)

    # move finished pdf file to other folder and clean up temp
    os.rename(app.config['SONGBOOK_TEMP_FOLDER'] + filename + '.pdf',
              app.config['SONGBOOK_DONE_FOLDER'] + filename + '.pdf')

    # remove all aux files
    for fname in os.listdir(app.config['SONGBOOK_TEMP_FOLDER']):
        if fname.startswith(filename):
            os.remove(os.path.join(app.config['SONGBOOK_TEMP_FOLDER'], fname))

    return "download/{}.pdf".format(filename)
