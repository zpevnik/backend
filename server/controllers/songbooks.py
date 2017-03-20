from flask import g, request, jsonify, Blueprint

from server.app import app
from server.util import generate_random_filename, generate_tex_file, export_to_pdf
from server.util import validators

import os
import subprocess
import logging
logger = logging.getLogger(__name__)


api = Blueprint('songbooks', __name__,)


@api.route('/songbooks', methods=['GET', 'POST'])
def songbooks():
    ip = request.remote_addr

    if request.method == 'GET':
        #validators.authors_GET(data)

        #print request.headers['Content-Type']

        data = {}
        data['page'] = 1
        data['per_page'] = 2
        data['query'] = "kokos"

        page = data['page'] if 'page' in data else 0;
        per_page = data['per_page'] if 'per_page' in data else 30;

        result = g.model.songbooks.find_special(data['query'], page, per_page)
        print result
        return 'ok', 200
    else:
        data = request.get_json()
        validators.songbooks_POST(data)

        songbook = g.model.songbooks.create_songbook(data)

        return jsonify(link="songbooks/" + songbook.get_id()), 201

# TODO
@api.route('/songbooks/<songbook_id>', methods=['GET', 'PUT', 'DELETE'])
def songbook_single(songbook_id):
    ip = request.remote_addr
    data = request.get_json()

    return 'Ok', 200

# TODO
@api.route('/songbooks/<songbook_id>/song/<song_id>/variants/<variant_id>', methods=['POST','DELETE'])
def songbook_song_variants(songbook_id, song_id, variant_id):
    ip = request.remote_addr
    data = request.get_json()

    return 'Ok', 200

app.register_blueprint(api, url_prefix='/api/v1')
