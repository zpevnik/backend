import logging

from flask import g
from flask import request
from flask import jsonify
from flask import Blueprint

from server.app import app
from server.util import validators

logger = logging.getLogger(__name__)
api = Blueprint('authors', __name__,)


@api.route('/authors', methods=['GET', 'POST'])
def authors():
    if request.method == 'GET':
        data = {
            'query': request.args['query'] if 'query' in request.args and request.args['query'] is not None else "",
            'page': int(request.args['page']) if 'page' in request.args and request.args['page'] is not None else 0,
            'per_page': int(request.args['per_page']) if 'per_page' in request.args and request.args['per_page'] is not None else 30
        }
        validators.request_GET(data)

        result = g.model.authors.find_special(data['query'], data['page'], data['per_page'])
        response = []
        for res in result:
            response.append(res.get_serialized_data())

        return jsonify(response), 200

    else:
        data = request.get_json()

        validators.authors_POST(data)
        validators.author_nonexistence(data['firstname'], data['surname'])

        author = g.model.authors.create_author(data)

        return jsonify(link="authors/" + author.get_id()), 201


@api.route('/authors/<author_id>', methods=['GET', 'PUT', 'DELETE'])
def author_single(author_id):
    if request.method == 'GET':
        author = validators.author_existence(author_id)
        return jsonify(author.get_serialized_data()), 200

    elif request.method == 'PUT':
        data = request.get_json()
        author = validators.author_existence(author_id)

        if 'firstname' in data:
            author.set_firstname(data['firstname'])
        if 'surname' in data:
            author.set_surname(data['surname'])

        g.model.authors.save(author)
        return 'Ok', 200

    else:
        author = validators.author_existence(author_id)
        g.model.authors.delete(author)

        return 'Ok', 200

app.register_blueprint(api, url_prefix='/api/v1')
