#!/usr/bin/python
import subprocess

subprocess.call(['mkdir', 'server_data'])
subprocess.call(['mkdir', 'mongo_data'])

subprocess.call(['virtualenv', 'server_data'])
subprocess.call(['server_data/bin/pip', 'install', 'flask'])
subprocess.call(['server_data/bin/pip', 'install', 'flask-login'])
subprocess.call(['server_data/bin/pip', 'install', 'flask-wtf'])
subprocess.call(['server_data/bin/pip', 'install', 'flask-mail'])
subprocess.call(['server_data/bin/pip', 'install', 'flask-compress'])
subprocess.call(['server_data/bin/pip', 'install', 'gevent'])
subprocess.call(['server_data/bin/pip', 'install', 'gevent-websocket'])
subprocess.call(['server_data/bin/pip', 'install', 'gevent-socketio'])
subprocess.call(['server_data/bin/pip', 'install', 'pymongo'])
subprocess.call(['server_data/bin/pip', 'install', 'colorlog'])
subprocess.call(['server_data/bin/pip', 'install', 'zeep'])
