from flask import g
from flask import jsonify
from flask import request
from flask import Blueprint
from flask_login import current_user
from flask_login import login_required

from server.app import app
from server.util import validators
from server.util import log_event

from server.constants import EVENTS

api = Blueprint('interpreters', __name__)


@api.route('/interpreters', methods=['GET', 'POST'])
@login_required
def interpreters():
    if request.method == 'GET':
        result = g.model.interpreters.find()
        response = []
        for res in result:
            response.append(res.get_serialized_data())

        return jsonify(response), 200

    else:
        data = request.get_json()
        validators.json_request(data)

        data = validators.interpreters_request(data)
        validators.interpreter_nonexistence(data['name'])

        interpreter = g.model.interpreters.create_interpreter(data)
        log_event(EVENTS.INTERPRETER_NEW, current_user.get_id(), data)

        return jsonify(link='interpreters/{}'.format(interpreter.get_id())), 201, \
              {'location': '/interpreters/{}'.format(interpreter.get_id())}


@api.route('/interpreters/<interpreter_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def interpreter_single(interpreter_id):
    interpreter = validators.interpreter_existence(interpreter_id)

    if request.method == 'GET':
        return jsonify(interpreter.get_serialized_data()), 200

    elif request.method == 'PUT':
        interpreter = validators.interpreter_existence(interpreter_id)

        data = request.get_json()
        validators.json_request(data)
        data = validators.interpreters_request(data)

        interpreter.set_data(data)

        data['interpreter_id'] = interpreter_id
        g.model.interpreters.save(interpreter)
        log_event(EVENTS.INTERPRETER_EDIT, current_user.get_id(), data)

        return jsonify(interpreter.get_serialized_data()), 200

    else:
        g.model.interpreters.delete(interpreter)
        log_event(EVENTS.INTERPRETER_DELETE, current_user.get_id(), interpreter_id)

        return jsonify(), 204


app.register_blueprint(api, url_prefix='/api/v1')
