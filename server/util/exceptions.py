class ClientException(Exception):

    def __init__(self, message, status_code):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code


class RequestException(Exception):

    def __init__(self, message, status_code):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code


class TranslationException(Exception):

    def __init__(self, message, status_code):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code


class CompilationException(Exception):

    def __init__(self, message, status_code):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code


class ValidationException(Exception):

    def __init__(self, message, status_code, errors=None):
        Exception.__init__(self)
        self._errors = errors
        self.message = message
        self.status_code = status_code

    def set_errors(self, errors):
        self._errors = errors

    def add_error(self, field, code, message):
        if self._errors is None:
            self._errors = []

        self._errors.append({'field': field, 'code': code, 'message': message})

    def get_json(self):
        json = {'message': self.message}
        if self._errors is not None:
            json['errors'] = self._errors
        return json
