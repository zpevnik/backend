#!/usr/bin/python
import subprocess

subprocess.call(['mongod', '--smallfiles', '--dbpath', 'mongo_data/'])
