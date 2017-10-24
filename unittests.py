#!./__venv__/bin/python3.6

import os
import unittest

if __name__ == '__main__':
    # set testing database environment variable
    os.environ['MONGODB_UNITTEST_URI'] = 'mongodb://localhost:27017/unittest'

    # impoort tests and run them
    from tests import *
    unittest.main()

    # disable testing environment
    del os.environ['MONGODB_UNITTEST_URI']
