from server.constants import EVENTS

class AppException(Exception):

    def __init__(self, exp_type, message, status_code, data=None):
        Exception.__init__(self)
        self.status_code = status_code
        self.exp_type = exp_type
        self.message = message
        self.data = data

    # returns exception data in one dictionary
    def get_exception(self):
        data = {'message': self.message}
        if self.data is not None:
            data['data'] = self.data
        if self.extype is not None:
            data['exp_type'] = self.exp_type

        return data
