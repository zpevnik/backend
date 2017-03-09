from flask import g, request, Blueprint

from server.app import app
from server.util import generate_random_filename, generate_tex_file, export_to_pdf
from server.util import validators

import os
import subprocess
import logging
logger = logging.getLogger(__name__)


api = Blueprint('songs', __name__,)

@api.route('/songs', methods=['POST'])
def songs():
    ip = request.remote_addr
    data = request.get_json()

    logger.info('New song is incoming from %s!' % ip)

    validators.songs_request_valid(data)

    song = g.model.songs.create_song(data)
    filename = generate_random_filename()

    song.generate_tex(filename)
    generate_tex_file(filename)

    exported = export_to_pdf(filename)
    return exported, 200

app.register_blueprint(api, url_prefix='/api/v1')
