
class Skautis(object):

    def __init__(self, secret):
        print secret

        self._server = secret
        self._test = "Test"

    def set_this(self):
        self._test = "No"

    def test(self):
        print self._test


class SkautisApi(object):

    def __init__(self, secret):
        print secret

        self._server = secret
        self._test = "Test"

    def set_this(self):
        self._test = "No"

    def test(self):
        print self._test
