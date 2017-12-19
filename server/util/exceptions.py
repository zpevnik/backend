class AppException(Exception):

    def __init__(self, exp_type, status_code, error=None):
        Exception.__init__(self)
        self.status_code = status_code
        self.exp_type = exp_type
        self.errors = []

        if (error):
            self.add_error(*error)

    # add error into error array
    def add_error(self, exp_code, message, data=None):
        self.errors.append({'code': exp_code, 'message': message, 'data': data})

    # returns exception data in one dictionary
    def get_exception(self):
        return self.errors
