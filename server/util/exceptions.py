class AppException(Exception):
    status_code = 422

    def __init__(self, typeName, code, message, status_code=None):
        Exception.__init__(self)
        self.type = typeName
        self.code = code
        self.message = message
        if status_code is not None:
            self.status_code = status_code