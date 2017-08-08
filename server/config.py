"""Configuration file for Zpevnik application"""

from os import getenv

VERSION = '0.1'
APP_NAME = 'Skautský zpěvník'
SECRET_KEY = 'q@yqlen+yr03d$z8mcbyx005a&'

SERVER_PORT = int(getenv('PORT', 5010))

MONGODB_URI = getenv('MONGODB_URI', 'mongodb://localhost:27017/zpevnik')

SKAUTIS = {
    'TEST': False,
    'APPID': getenv('SKAUTIS_APPID', 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx')
}
