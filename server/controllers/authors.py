from flask import g
from flask import jsonify
from flask import request
from flask import Blueprint
from flask_cors import cross_origin
from flask_login import current_user
from flask_login import login_required

from server.app import app
from server.util import validators

from server.constants import EVENTS


api = Blueprint('authors', __name__,)


@api.route('/authors', methods=['GET', 'POST'])
@login_required
def authors():
    if request.method == 'GET':
        data = validators.handle_GET_request(request.args)
        result = g.model.authors.find_special(data['query'], data['page'], data['per_page'])
        response = []
        for res in result:
            response.append(res.get_serialized_data())

        return jsonify(response), 200

    else:
        data = request.get_json()
        validators.json_request(data)

        data = validators.authors_request(data)
        validators.author_nonexistence(data['name'])

        author = g.model.authors.create_author(data)

        g.model.logs.create_log({'event': EVENTS.AUTHOR_NEW,
                                 'user': current_user.get_id(),
                                 'data': data})

        return jsonify(link='authors/{}'.format(author.get_id())), 201, \
              {'location': '/authors/{}'.format(author.get_id())}


@api.route('/authors/<author_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def author_single(author_id):
    author = validators.author_existence(author_id)

    if request.method == 'GET':    
        return jsonify(author.get_serialized_data()), 200

    elif request.method == 'PUT':
        author = validators.author_existence(author_id)

        data = request.get_json()
        validators.json_request(data)
        data = validators.authors_request(data)

        author.set_data(data)

        data['author_id'] = author_id
        g.model.authors.save(author)
        g.model.logs.create_log({'event': EVENTS.AUTHOR_EDIT,
                                 'user': current_user.get_id(),
                                 'data': data})

        return jsonify(author.get_serialized_data()), 200

    else:
        g.model.authors.delete(author)
        g.model.logs.create_log({'event': EVENTS.AUTHOR_DELETE,
                                 'user': current_user.get_id(),
                                 'data': author_id})

        return jsonify(), 204

app.register_blueprint(api, url_prefix='/api/v1')
