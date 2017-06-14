# -*- coding: utf-8 -*-

from flask import g
from flask import request
from flask import jsonify
from flask import Blueprint

from server.app import app
from server.util import validators

api = Blueprint('songbooks', __name__,)


@api.route('/songbooks', methods=['GET', 'POST'])
@login_required
def songbooks():
    if request.method == 'GET':
        data = {
            'query': request.args['query'] if 'query' in request.args and request.args['query'] is not None else "",
            'page': int(request.args['page']) if 'page' in request.args and request.args['page'] is not None else 0,
            'per_page': int(request.args['per_page']) if 'per_page' in request.args and request.args['per_page'] is not None else 30
        }
        validators.request_GET(data)

        result = g.model.songbooks.find_special(data['query'], data['page'], data['per_page'])
        response = []
        for res in result:
            response.append(res.get_serialized_data())

        return jsonify(response), 200

    else:
        data = request.get_json()

        validators.json_request(data)
        validators.songbooks_request(data)
        songbook = g.model.songbooks.create_songbook(data)

        return jsonify(link='songbooks/{}'.format(songbook.get_id())), 201, \
              {'location': '/songbooks/{}'.format(songbook.get_id())}


@api.route('/songbooks/<songbook_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def songbook_single(songbook_id):
    if request.method == 'GET':
        songbook = validators.songbook_existence(songbook_id)

        if request.headers['Content-Type'] == 'application/pdf':
            filename = generate_random_filename()

            for song_x in songbook.get_songs():
                song = validators.song_existence(song_x['song'])
                song.generate_tex(filename, variant_id)

            generate_tex_file(filename)
            exported = export_to_pdf(filename)
            return exported, 200

        return jsonify(songbook.get_serialized_data()), 200

    elif request.method == 'PUT':
        data = request.get_json()
        songbook = validators.songbook_existence(songbook_id)

        validators.json_request(data)
        validators.songbooks_request(data)

        if 'title' in data:
            songbook.set_title(data['title'])

        g.model.songbooks.save(songbook)
        return jsonify(songbook.get_serialized_data()), 200

    else:
        songbook = validators.songbook_existence(songbook_id)
        g.model.songbooks.delete(songbook)
        return jsonify(), 204

# FIXME
@api.route('/songbooks/<songbook_id>/song/<song_id>/variants/<variant_id>', methods=['POST', 'DELETE'])
@login_required
def songbook_song_variants(songbook_id, song_id, variant_id):
    if request.method == 'POST':
        songbook = validators.songbook_existence(songbook_id)
        song = validators.song_existence(song_id)
        song.find_variant(variant_id)

        songbook.add_song(song_id, variant_id)
        g.model.songbooks.save(songbook)
        return jsonify({'message': 'Píseň byla úspěšně přidána do zpěvníku.'}), 200

    else:
        songbook = validators.songbook_existence(songbook_id)
        song = validators.song_existence(song_id)
        song.find_variant(variant_id)

        songbook.remove_song(song_id, variant_id)
        g.model.songbooks.save(songbook)
        return jsonify(), 204

app.register_blueprint(api, url_prefix='/api/v1')
