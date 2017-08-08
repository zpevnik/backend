from flask import g
from flask import jsonify
from flask import request
from flask import Blueprint
from flask_cors import cross_origin
from flask_login import current_user
from flask_login import login_required

from server.app import app
from server.util import generate_random_filename
from server.util import generate_tex_file
from server.util import export_to_pdf
from server.util import validators

from server.constants import EVENTS


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

        g.model.logs.create_log({'event': EVENTS.SONG_NEW,
                                 'user': current_user.get_id(),
                                 'data': data})

        return jsonify(link='songs/{}'.format(song.get_id())), 201, \
              {'location': '/songs/{}'.format(song.get_id())}


@api.route('/songs/<song_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def song_single(song_id):
    if request.method == 'GET':
        song = validators.song_existence(song_id)

        if request.headers['Content-Type'] == 'application/pdf':
            filename = generate_random_filename()
            song.generate_tex(filename)

            generate_tex_file(filename)
            exported = export_to_pdf(filename)
            return exported, 200

        return jsonify(song.get_serialized_data()), 200

    elif request.method == 'PUT':
        data = request.get_json()
        song = validators.song_existence(song_id)

        validators.json_request(data)
        validators.songs_request(data)

        if 'title' in data:
            song.set_title(data['title'])
        if 'text' in data:
            song.set_text(data['text'])

        for author in data['authors']['music']:
            validators.author_existence(author)
        for author in data['authors']['lyrics']:
            validators.author_existence(author)
        for author in data['interpreters']:
            validators.author_existence(author)

        song.set_authors(data['authors'])
        song.set_interpreters(data['interpreters'])

        data['song_id'] = song_id

        g.model.songs.save(song)
        g.model.logs.create_log({'event': EVENTS.SONG_EDIT,
                                 'user': current_user.get_id(),
                                 'data': data})

        return jsonify(song.get_serialized_data()), 200

    else:
        song = validators.song_existence(song_id)
        g.model.songs.delete(song)
        g.model.logs.create_log({'event': EVENTS.SONG_DELETE,
                                 'user': current_user.get_id(),
                                 'data': song_id})

        return jsonify(), 204

app.register_blueprint(api, url_prefix='/api/v1')
