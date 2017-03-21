from flask import g
from flask import request
from flask import jsonify
from flask import Blueprint

from server.app import app
from server.util import validators

api = Blueprint('songbooks', __name__,)


@api.route('/songbooks', methods=['GET', 'POST'])
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
            print res

        return jsonify(response), 200

    else:
        data = request.get_json()

        validators.songbooks_POST(data)
        songbook = g.model.songbooks.create_songbook(data)

        return jsonify(link="songbooks/" + songbook.get_id()), 201


@api.route('/songbooks/<songbook_id>', methods=['GET', 'PUT', 'DELETE'])
def songbook_single(songbook_id):
    if request.method == 'GET':
        songbook = validators.songbook_existence(songbook_id)
        return jsonify(songbook.get_serialized_data()), 200

    elif request.method == 'PUT':
        data = request.get_json()
        songbook = validators.songbook_existence(songbook_id)

        if 'title' in data:
            songbook.set_title(data['title'])

        g.model.songbooks.save(songbook)
        return 'Ok', 200

    else:
        songbook = validators.songbook_existence(songbook_id)
        g.model.songbooks.delete(songbook)
        return 'Ok', 200


@api.route('/songbooks/<songbook_id>/song/<song_id>/variants/<variant_id>', methods=['POST', 'DELETE'])
def songbook_song_variants(songbook_id, song_id, variant_id):
    if request.method == 'POST':
        songbook = validators.songbook_existence(songbook_id)
        song = validators.song_existence(song_id)
        song.find_variant(variant_id)

        songbook.add_song(song_id, variant_id)
        g.model.songbooks.save(songbook)
        return 'Ok', 200

    else:
        songbook = validators.songbook_existence(songbook_id)
        song = validators.song_existence(song_id)
        song.find_variant(variant_id)

        songbook.remove_song(song_id, variant_id)
        g.model.songbooks.save(songbook)
        return 'Ok', 204

app.register_blueprint(api, url_prefix='/api/v1')
