import os
import subprocess

from server.util.exceptions import AppException


def generate_tex_file(filename):
    with open('songs/sample/sample.tex', 'r') as sample_file:
        filedata = sample_file.read()

    filedata = filedata.replace('$filename$', filename)
    with open('songs/temp/' + filename + '.tex', 'w') as temp_file:
        temp_file.write(filedata)

def export_to_pdf(filename):

    def error(err, output):
        error = "Error during "+err+":\n"
        for line in output.split("\n"):
            if line.startswith("!"):
                error += line + "\n"

        raise AppException('error', 'compilation_error', error, status_code=422)

    process = subprocess.Popen(["pdflatex", "-halt-on-error", filename + ".tex"],
                               stdout=subprocess.PIPE, cwd='songs/temp')
    output = process.communicate()[0]
    exit_code = process.wait()

    if exit_code:
        error("pdf compilation", output)

    process = subprocess.Popen(["../songidx", filename + ".sxd", filename + ".sbx"],
                               stdout=subprocess.PIPE, cwd='songs/temp')
    output = process.communicate()[0]
    exit_code = process.wait()

    if exit_code:
        error("index generation", output)

    process = subprocess.Popen(["pdflatex", "-halt-on-error", filename + ".tex"],
                               stdout=subprocess.PIPE, cwd='songs/temp')
    output = process.communicate()[0]
    exit_code = process.wait()

    if exit_code:
        error("pdf compilation", output)

    # move finished pdf file to other folder and clean up temp
    os.rename('songs/temp/' + filename + '.pdf', 'songs/done/' + filename + '.pdf')
    for fname in os.listdir('songs/temp'):
        if fname.startswith(filename):
            os.remove(os.path.join('songs/temp', fname))

    if not os.path.isfile("songs/done/" + filename + ".pdf"):
        raise AppException('error', 'file_existence_error',
                           'Final pdf file does not exist.', status_code=422)

    return "songs/done/" + filename + ".pdf"
