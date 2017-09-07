from flask import g
from flask import jsonify
from flask import request
from flask import Blueprint
from flask_login import current_user
from flask_login import login_required

from server.app import app
from server.util import validators

#from server.constants import EVENTS


api = Blueprint('interpreters', __name__,)

@api.route('/interpreters', methods=['GET', 'POST'])
@login_required
def interpreters():
    if request.method == 'GET':
        #data = validators.handle_GET_request(request.args)
        #result = g.model.interpreters.find_special(data['query'], data['page'], data['per_page'])
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

#        g.model.logs.create_log({'event': EVENTS.AUTHOR_NEW,
#                                 'user': current_user.get_id(),
#                                 'data': data})

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
#        g.model.logs.create_log({'event': EVENTS.AUTHOR_EDIT,
#                                 'user': current_user.get_id(),
#                                 'data': data})

        return jsonify(interpreter.get_serialized_data()), 200

    else:
        g.model.interpreters.delete(interpreter)
#        g.model.logs.create_log({'event': EVENTS.AUTHOR_DELETE,
#                                 'user': current_user.get_id(),
#                                 'data': author_id})

        return jsonify(), 204

app.register_blueprint(api, url_prefix='/api/v1')
