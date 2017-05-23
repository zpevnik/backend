#!/usr/bin/python
import subprocess

subprocess.call(['mkdir', 'venv'])
subprocess.call(['mkdir', 'mongo_data'])

subprocess.call(['virtualenv', 'venv'])
subprocess.call(['venv/bin/pip', 'install', 'flask'])
subprocess.call(['venv/bin/pip', 'install', 'flask-login'])
subprocess.call(['venv/bin/pip', 'install', 'flask-wtf'])
subprocess.call(['venv/bin/pip', 'install', 'flask-mail'])
subprocess.call(['venv/bin/pip', 'install', 'flask-compress'])
subprocess.call(['venv/bin/pip', 'install', 'gevent'])
subprocess.call(['venv/bin/pip', 'install', 'gevent-websocket'])
subprocess.call(['venv/bin/pip', 'install', 'gevent-socketio'])
subprocess.call(['venv/bin/pip', 'install', 'pymongo'])
subprocess.call(['venv/bin/pip', 'install', 'colorlog'])
subprocess.call(['venv/bin/pip', 'install', 'zeep'])
