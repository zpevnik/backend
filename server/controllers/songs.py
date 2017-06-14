# -*- coding: utf-8 -*-

from flask import g
from flask import jsonify
from flask import request
from flask import Blueprint

from server.app import app
from server.util import generate_random_filename
from server.util import generate_tex_file
from server.util import export_to_pdf
from server.util import validators

api = Blueprint('songs', __name__,)


@api.route('/songs', methods=['GET', 'POST'])
@login_required
def songs():
    if request.method == 'GET':
        data = {
            'query': request.args['query'] if 'query' in request.args and request.args['query'] is not None else "",
            'page': int(request.args['page']) if 'page' in request.args and request.args['page'] is not None else 0,
            'per_page': int(request.args['per_page']) if 'per_page' in request.args and request.args['per_page'] is not None else 30
        }
        validators.request_GET(data)

        result = g.model.songs.find_special(data['query'], data['page'], data['per_page'])
        response = []
        for res in result:
            response.append(res.get_serialized_data())

        return jsonify(response), 200

    else:
        data = request.get_json()

        validators.json_request(data)
        validators.songs_request(data)
        song = g.model.songs.create_song(data)

        return jsonify(link='songs/{}'.format(song.get_id())), 201, \
              {'location': '/songs/{}'.format(song.get_id())}


@api.route('/songs/<song_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def song_single(song_id):
    if request.method == 'GET':
        song = validators.song_existence(song_id)
        return jsonify(song.get_serialized_data()), 200

    elif request.method == 'PUT':
        data = request.get_json()
        song = validators.song_existence(song_id)

        validators.json_request(data)
        validators.songs_request(data)

        if 'title' in data:
            song.set_title(data['title'])

        g.model.songs.save(song)
        return jsonify(song.get_serialized_data()), 200

    else:
        song = validators.song_existence(song_id)
        g.model.songs.delete(song)
        return jsonify(), 204


@api.route('/songs/<song_id>/variants', methods=['GET', 'POST'])
@login_required
def song_variants(song_id):
    if request.method == 'GET':
        song = validators.song_existence(song_id)
        variants = song.get_variants()

        response = []
        for variant in variants:
            response.append({
                'id': variant.get_id(),
                'song': song.get_id(),
                'title': variant.get_title(),
                'chords': variant.get_text()
            })

        return jsonify(response), 200

    else:
        data = request.get_json()
        song = validators.song_existence(song_id)

        validators.json_request(data)
        validators.variants_request(data)

        variant = song.create_variant(data)
        g.model.songs.save(song)

        return jsonify(link='songs/{}/variants/{}'.format(song.get_id(), variant.get_id())), 201, \
              {'location': '/songs/{}/variants/{}'.format(song.get_id(), variant.get_id())}


@api.route('/songs/<song_id>/variants/<variant_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def song_variant_single(song_id, variant_id):
    if request.method == 'GET':
        song = validators.song_existence(song_id)

        if request.headers['Content-Type'] == 'application/pdf':
            filename = generate_random_filename()

            song.generate_tex(filename, variant_id)
            generate_tex_file(filename)

            exported = export_to_pdf(filename)
            return exported, 200

        variant = song.find_variant(variant_id)
        response = {
            'id': variant.get_id(),
            'song': song.get_id(),
            'title': variant.get_title(),
            'chords': variant.get_text()
        }
        return jsonify(response), 200

    elif request.method == 'PUT':
        data = request.get_json()
        song = validators.song_existence(song_id)
        variant = song.find_variant(variant_id)

        validators.json_request(data)
        validators.variants_request(data)

        if 'title' in data:
            variant.set_title(data['title'])
        if 'chords' in data:
            variant.set_text(data['text'])

        g.model.songs.save(song)

        return jsonify(variant.get_serialized_data()), 200

    else:
        song = validators.song_existence(song_id)
        song.delete_variant(variant_id)

        g.model.songs.save(song)
        return jsonify(), 204


@api.route('/songs/<song_id>/authors', methods=['GET'])
@login_required
def song_authors(song_id):
    song = validators.song_existence(song_id)
    author_ids = song.get_authors()

    authors = []
    for author_id in author_ids:
        author = g.model.authors.find_one(author_id=author_id)
        authors.append(author.get_serialized_data())

    return jsonify(authors), 200


@api.route('/songs/<song_id>/authors/<author_id>', methods=['POST', 'DELETE'])
@login_required
def song_author_singe(song_id, author_id):
    if request.method == 'POST':
        song = validators.song_existence(song_id)

        validators.author_existence(author_id)
        song.add_author(author_id)

        g.model.songs.save(song)
        return jsonify({'message': 'Přiřazení autora proběhlo úspěšně.'}), 200

    else:
        song = validators.song_existence(song_id)

        song.remove_author(author_id)
        g.model.songs.save(song)
        return jsonify(), 204


app.register_blueprint(api, url_prefix='/api/v1')
