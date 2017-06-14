"""Configuration file for Zpevnik application"""

from os import getenv

VERSION = '0.1'
APP_NAME = 'Skautský zpěvník'

DEVELOPMENT = True
SERVER_PORT = int(getenv('PORT', 5010))

MONGODB_URI = getenv('MONGODB_URI', 'mongodb://localhost:27017/zpevnik')

SKAUTIS = {
	'TEST': True,
	'APPID': getenv('SKAUTIS_APPID', 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx')
}
