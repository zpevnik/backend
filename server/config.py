"""Configuration file for Zpevnik application"""

from os import getenv

VERSION = '0.3'
APP_NAME = 'Skautský zpěvník'

# Switches applicataion to maintenance mode (site offline)
MAINTENANCE_MODE = False

SERVER_PORT = int(getenv('PORT', 5010))
SERVER_IP = getenv('SERVER_IP', '127.0.0.1')

SECRET_KEY = getenv('SECRET_KEY', 'test_secret')
MONGODB_URI = getenv('MONGODB_UNITTEST_URI',
                     getenv('MONGODB_URI', 'mongodb://localhost:27017/zpevnik'))

SONGBOOK_TEMP_FOLDER = 'songs/temp/'
SONGBOOK_DONE_FOLDER = 'songs/done/'

SKAUTIS = {
    'TEST': getenv('SKAUTIS_TEST', False),
    'APPID': getenv('SKAUTIS_APPID', '3d59cc18-b2b9-46d7-b2e7-9f480f99553d')
}
