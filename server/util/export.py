import os
import pystache
import subprocess

from server.app import app
from server.util import validators
from server.util.misc import generate_random_filename
from server.util.exceptions import AppException

from server.constants import EVENTS
from server.constants import EXCODES
from server.constants import STRINGS
from server.constants import DEFAULTS


def export_songbook(songbook):
    # check if songbook is cached
    if songbook.is_cached():
        filename = songbook.get_cached_file(extend=True)

        # check if file really exists
        if os.path.isfile(app.config['SONGBOOK_DONE_FOLDER'] + filename + ".pdf"):
            return {'link': "download/{}.pdf".format(filename), 'log': {}}

    # start export process
    filename = generate_random_filename()

    # create instance of pystache renderer
    renderer = pystache.Renderer(string_encoding='utf-8', search_dirs=app.config['SONGBOOK_TEMPLATE_FOLDER'])

    # generate song sbd file
    with open(app.config['SONGBOOK_TEMP_FOLDER'] + filename + '.sbd', 'ab') as file:
        for song_obj in songbook.get_songs():
            variant = validators.song_variant_existence(song_obj['variant_id'])
            template = variant.get_output_template()
            file.write(renderer.render(template).encode('utf8'))

    # generate songbook tex file
    with open(app.config['SONGBOOK_TEMP_FOLDER'] + filename + '.tex', 'wb') as file:
        template = songbook.get_output_template()
        template.set_filename(filename)
        file.write(renderer.render(template).encode('utf8'))

    # export songbook to pdf file
    link = export_to_pdf(filename)

    # cache songbook
    songbook.cache_file(filename)
    return {'link': link}


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
